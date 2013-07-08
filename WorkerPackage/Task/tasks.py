import shutil
import subprocess
from time import sleep
import os
from celery import Celery

# RUN CELERY WORKER :
# celery worker -Q openmalaria

# Point to rabbitMQ
import psycopg2
import re
import sys
from settings import openmalaria_data_dir, om_exe, DATABASES, BROKER_URL

sys.path.append(os.getcwd())

#Greg changed the order of these (backend and broker swapped) to remove a warning
celery = Celery('celeryOpenmalaria', broker=BROKER_URL, backend='amqp')

@celery.task(name='runOpenMalaria',ignore_result=True)
def runOpenMalaria(run_id):
    sleep(5)
    # Connect to the db
    
    dbconn = psycopg2.connect(host=DATABASES['default']['HOST'], user=DATABASES['default']['USER'],password=DATABASES['default']['PASSWORD'],database=DATABASES['default']['NAME'])
    cursor = dbconn.cursor()

    # Fetch the file from the database
    cursor.execute("""
            SELECT contents
            from frontend_simulationrun
            where id = %(id)s
        """ ,{'id': run_id})

    xml = str(cursor.fetchone()[0])

    # Prepare the simulation folder
    simulation_dir = os.path.join(openmalaria_data_dir,str(run_id))

    # Remove the directory if it already exists
    if os.path.exists(simulation_dir):
        shutil.rmtree(simulation_dir)

    # Copy the common
    common_dir =  os.path.join(openmalaria_data_dir,"common")
    shutil.copytree(common_dir, simulation_dir)

    # Write the XML
    file = open(os.path.join(simulation_dir,"scenario.xml"),'w')
    file.write(xml)
    file.close()

    # Run OpenMalaria
    errorfile = open(os.path.join(simulation_dir,'error.txt'),'w')
    omprocess = subprocess.Popen([om_exe,"--scenario",'scenario.xml'], shell=False,cwd=simulation_dir,stdout=subprocess.PIPE, stderr=errorfile)

    lastpercentage = 0

    while True:
        # Read 20 characters
        # Readline does not work here because of OpenMalaria refreshing the same line over and over
        out = omprocess.stdout.read(20)

        # If we do not have an output and the subprocess is done
        # That mean we are done
        if out == '' and omprocess.poll() is not None:
            break
        if out != '':
            # Extract the % (can be more than one)
            percentages =  re.findall(r'\d+',out)
            # If we extracted % take the last one of the list and store it in the db
            if percentages is not None and len(percentages) > 0:
                newpercentage =  percentages[len(percentages)-1]
                if lastpercentage != newpercentage:
                    lastpercentage = newpercentage
                    # Update the state
                    cursor.execute("""
                        UPDATE frontend_simulationrun
                        SET status = %s
                        Where id = %s
                        """,[newpercentage,run_id])
                    dbconn.commit()
        sys.stdout.flush()
    omprocess.communicate()
    errorfile.close()


    # Send back the results (in any)
    if not os.path.exists(os.path.join(simulation_dir,"output.txt")):
        # No output = error during the processing
        # Find the error if any
        if not os.path.exists(os.path.join(simulation_dir,"error.txt")):
            error = 'Unknown Error'
        else:
            errorfile = open(os.path.join(simulation_dir,"error.txt"),'r')
            error = errorfile.read()
            errorfile.close()
        # Load the error
        cursor.execute("""
            UPDATE frontend_simulationrun
            SET status = -1,
            message = %s
            Where id = %s
            """,[unicode(error),run_id])
    else:
        result = open(os.path.join(simulation_dir,"output.txt"),'r').read()
        cts_out = open(os.path.join(simulation_dir, "ctsout.txt"), 'r').read()
        cursor.execute("""
        UPDATE frontend_simulationrun
        SET sim_results = %s, sim_cts_out = %s, finished = true
        Where id = %s
        """,[unicode(result,'utf-8'),unicode(cts_out,'utf-8'),run_id])

    dbconn.commit()

    # Close the db connection
    cursor.close()
    dbconn.close()

    # Cleanup
    try:
        shutil.rmtree(simulation_dir)
    except Exception as detail:
        print 'An exception occurred while trying to remove the simulation directory:'
        print detail




