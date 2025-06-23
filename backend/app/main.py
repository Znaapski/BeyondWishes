from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .libs.CouchDBClient import CouchDBClient
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import os
import json

#region CONSTANTS
PATIENTS_DB = "patients"
#endregion

#region CLASSES
class Relative(BaseModel):
    first_name: str
    last_name: str
    relation: str
    email: str | None = None
    phone_number: str | None = None

class Patient(BaseModel):
    first_name: str
    last_name: str
    picture: str | None = None
    birthdate: str
    sex: str
    diagnosis: str
    prognosis: str
    wish: str
    relatives: list[Relative] = []

class PatientFromDB(Patient):
    id: str | None = Field(alias="_id", default=None)
    rev: str | None = Field(alias="_rev", default=None)

class Message(BaseModel):
    message: str

#endregion

#region FASTAPI/COUCHDB SETUP
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

couchdb_client = CouchDBClient(url="http://couchdb:5984")
#endregion

#region FASTAPI EVENTS
@app.on_event("startup")
async def startup_event():
    try:
        couchdb_client.createDatabase(PATIENTS_DB)
    except Exception:
        pass
#endregion

#region API ENDPOINTS

@app.get("/patients/")
async def list_patients() -> list[PatientFromDB]:
    patient_keys = couchdb_client.listDocuments(PATIENTS_DB)
    patients = []
    for key in patient_keys:
        patient = couchdb_client.getDocument(PATIENTS_DB, key)
        patients.append(patient)
    return patients

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str) -> PatientFromDB:
    try:
        patient = couchdb_client.getDocument(PATIENTS_DB, patient_id)  
        return patient
    except Exception:
        raise HTTPException(status_code=404, detail="Patient does not exist")

@app.post("/patients/")
async def create_patient(patient: Patient) -> PatientFromDB:
    patient_as_json = jsonable_encoder(patient)
    key = couchdb_client.addDocument(PATIENTS_DB, patient_as_json) 
    new_patient = couchdb_client.getDocument(PATIENTS_DB, key)
    return  new_patient


@app.post("/patients/{patient_id}/notify-relatives")
async def notify_relatives(patient_id: str) -> Message:
    patient: PatientFromDB | None = None
    
    try:
        patient_document = couchdb_client.getDocument(PATIENTS_DB, patient_id)
        patient = PatientFromDB.parse_obj(patient_document)
    except Exception:
        raise HTTPException(status_code=404, detail="Patient does not exist")

    wish = patient.wish
    patient_name = f"{patient.first_name} {patient.last_name}"
    for relative in patient.relatives:
        recipient_name = f"{relative.first_name} {relative.last_name}"
        email = relative.email
        
        result = send_email(recipient_email=email, recipient_name=recipient_name, dead_name=patient_name, death_wish=wish)
        if not result:
            raise HTTPException(status_code=500, detail="Email could not be sent.")
        
    return {"message": "Wish submitted and email sent successfully."}

# TODO: Enable only in DEV
@app.post("/populate")
async def populate():
    path = os.path.abspath("./app/PatientModels")
    print("PATH: ", path)
    
    # List dir
    files = os.listdir(path)
    print('FILES: ', files)
    
    # Iterate over the files
    for file in files:
        with open(os.path.join(path, file), "r") as f:
            patient = json.load(f)
            print(patient)
            key = couchdb_client.addDocument(PATIENTS_DB, patient)
            print("Added patient to couchdb with key: ", key)

# Need to double check this code...
@app.put("/patients")
async def update_patient(patient: PatientFromDB):
    patient_as_json = jsonable_encoder(patient)
    couchdb_client.replaceDocument(PATIENTS_DB, patient_as_json)
    return couchdb_client.getDocument(PATIENTS_DB, patient.id)
#endregion

#region utils

def send_email(recipient_email: str, recipient_name: str, dead_name: str, death_wish: str):
    sender_email = "test"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Notification of Last Wish Submission'

    message_body = f"""Dearest {recipient_name},
It is with a heavy heart that we convey the final wishes of {dead_name}:

"{death_wish}"

May their memory be a blessing.

With deepest sympathies,
The beyond wishes team
    """
    message.attach(MIMEText(message_body, 'plain'))

    try:
        with smtplib.SMTP(host="mailbox", port=1025) as smtp:
            smtp.send_message(message)
            return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False

#endregion