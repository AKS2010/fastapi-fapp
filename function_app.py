import azure.functions as func
import  datetime
import logging

from WrapperFunction import app as fastapi_app

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="mytimer")
@app.schedule(schedule="* 1 * * * *", 
              arg_name="mytimer",
              run_on_startup=True) 
def test_function(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)