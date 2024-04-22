from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, date
class Patient(BaseModel):
    id: int
    name: str
    age: int
    sex: str
    weight: float
    height: float
    phone: str

class Doctor(BaseModel):
    id: int
    name: str
    specialization: str
    phone: str
    is_available: bool = True

class Appointment(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date: datetime
    complete: bool = False

app = FastAPI()

patients_data: Dict[int, Patient] = {}
doctors_data: Dict[int, Doctor] = {}
appointments_data: Dict[int, Appointment] = {}
appointment_id_counter = 0

@app.post("/patients/", response_model=Patient)
def create_patient(patient: Patient):
    if patient.id in patients_data:
        raise HTTPException(status_code=400, detail=f"Patient with id, {patient.id}, already exists")
    patients_data[patient.id] = patient
    return patient

@app.get("/patients/", response_model=List[Patient])
def get_patients():
    return list(patients_data.values())

@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int):
    if patient_id not in patients_data:
        raise HTTPException(status_code=404, detail=f"No Patient Data found for id, {patient_id}")
    return patients_data[patient_id]

@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: Patient):
    if patient_id not in patients_data:
        raise HTTPException(status_code=404, detail=f"No Patient Data found for id, {patient_id}")
    patients_data[patient_id] = patient
    return patient

@app.delete("/patients/{patient_id}", response_model=Patient)
def delete_patient(patient_id: int):
    if patient_id not in patients_data:
        raise HTTPException(status_code=404, detail=f"No Patient Data found for id, {patient_id}")
    return patients_data.pop(patient_id)

@app.post("/doctors/", response_model=Doctor)
def create_doctor(doctor: Doctor):
    doctors_data[doctor.id] = doctor
    return doctor

@app.get("/doctors/", response_model=List[Doctor])
def get_doctors():
    return list(doctors_data.values())

@app.get("/doctors/{doctor_id}", response_model=Doctor)
def get_doctor(doctor_id: int):
    if doctor_id not in doctors_data:
        raise HTTPException(status_code=404, detail=f"No doctor data found for id, {doctor_id}")
    return doctors_data[doctor_id]

@app.put("/doctors/{doctor_id}", response_model=Doctor)
def update_doctor(doctor_id: int, doctor: Doctor):
    if doctor_id not in doctors_data:
        raise HTTPException(status_code=404, detail=f"No doctor data found for id, {doctor_id}")
    doctors_data[doctor_id] = doctor
    return doctor

@app.delete("/doctors/{doctor_id}", response_model=Doctor)
def delete_doctor(doctor_id: int):
    if doctor_id not in doctors_data:
        raise HTTPException(status_code=404, detail=f"No doctor data found for id, {doctor_id}")
    return doctors_data.pop(doctor_id)

@app.post("/appointments/", response_model=Appointment)
def create_appointment(patient_id: int, appointment_date: datetime, doctor_type: str):
    global appointment_id_counter

    if appointment_date.date() < date.today():
        raise HTTPException(status_code=400, detail="You cannot set appointments for past dates")

    available_doctors = [doctor for doctor_id, doctor in doctors_data.items() if doctor.is_available and doctor.specialization == doctor_type]
    
    for doctor in available_doctors:
        existing_appointment = None
        for appointment in reversed(list(appointments_data.values())):
            if appointment.doctor_id == doctor.id and appointment.date.date() == appointment_date.date():
                existing_appointment = appointment
                break
        
        if existing_appointment:
            if not existing_appointment.complete:
                raise HTTPException(status_code=400, detail=f"Appointment already scheduled with {doctor_type} on {appointment_date:%Y-%m-%d}.")
            

        appointment_id_counter += 1
        appointment = Appointment(
            id=appointment_id_counter,
            patient_id=patient_id,
            doctor_id=doctor.id,
            date=appointment_date
        )
        appointments_data[appointment_id_counter] = appointment
        return appointment
    
    raise HTTPException(status_code=404, detail=f"No {doctor_type} available for your appointment on {appointment_date:%Y-%m-%d}")



@app.put("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    if appointment_id not in appointments_data:
        raise HTTPException(status_code=404, detail=f"No Appointment found with id, {appointment_id}")
    if appointments_data[appointment_id].complete:
        raise HTTPException(status_code=404, detail=f"Appointment with id, {appointment_id}, already marked as completed")

    appointment = appointments_data[appointment_id]
    doctor_id = appointment.doctor_id
    doctor = doctors_data[doctor_id]
    appointments_data[appointment_id].complete = True
    print(f"{appointments_data}")

    return {"message": "Appointment Completed"}

@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int):
    if appointment_id not in appointments_data:
        raise HTTPException(status_code=404, detail=f"No Appointment found with id, {appointment_id}")
    if not appointments_data[appointment_id].complete:
        appointment = appointments_data.pop(appointment_id)
        return {"message": "Appointment canceled"}
    else:
        raise HTTPException(status_code=404, detail=f"You cannot cancel Completed Appointment")
        

@app.put("/doctors/{doctor_id}/availability")
def set_doctor_availability(doctor_id: int, is_available: bool):
    if doctor_id not in doctors_data:
        raise HTTPException(status_code=404, detail=f"No Doctor with id, {doctor_id}, was found")
    doctors_data[doctor_id].is_available = is_available
    return {"message": "Doctor availability updated"}


