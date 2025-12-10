from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List
import threading
import xml.etree.ElementTree as ET
import os

app = FastAPI(title="DW Server")

DW_NAME = os.getenv("DW_NAME", "DW-DEFAULT")

lock = threading.Lock()
employees: Dict[int, dict] = {}
next_id = 1


class Employee(BaseModel):
    name: str
    role: str
    salary: float


def to_xml(emp_or_list):
    if isinstance(emp_or_list, list):
        root = ET.Element("employees")
        for e in emp_or_list:
            el = ET.SubElement(root, "employee")
            for k, v in e.items():
                child = ET.SubElement(el, k)
                child.text = str(v)
    else:
        root = ET.Element("employee")
        for k, v in emp_or_list.items():
            child = ET.SubElement(root, k)
            child.text = str(v)
    return ET.tostring(root, encoding="utf-8")


@app.post("/employees")
def create_employee(emp: Employee):
    global next_id
    with lock:
        emp_id = next_id
        next_id += 1
        employees[emp_id] = {"id": emp_id, **emp.model_dump()}
    print(f"[{DW_NAME}] POST /employees -> created id={emp_id}")
    return {"status": "ok", "id": emp_id}


@app.put("/employees/{emp_id}")
def put_employee(emp_id: int, emp: Employee):
    with lock:
        employees[emp_id] = {"id": emp_id, **emp.model_dump()}
    print(f"[{DW_NAME}] PUT /employees/{emp_id}")
    return {"status": "ok", "id": emp_id}


@app.get("/employees/{emp_id}")
def get_employee(
    emp_id: int,
    format: str = Query("json", pattern="^(json|xml)$"),
):
    if emp_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp = employees[emp_id]
    print(f"[{DW_NAME}] GET /employees/{emp_id}?format={format}")

    if format == "json":
        return emp

    xml_bytes = to_xml(emp)
    return Response(content=xml_bytes, media_type="application/xml")


@app.get("/employees")
def list_employees(
    offset: int = 0,
    limit: int = 10,
    format: str = Query("json", pattern="^(json|xml)$"),
):
    all_emp: List[dict] = list(employees.values())
    selected = all_emp[offset: offset + limit]

    print(f"[{DW_NAME}] GET /employees?offset={offset}&limit={limit}&format={format}")

    if format == "json":
        return selected

    xml_bytes = to_xml(selected)
    return Response(content=xml_bytes, media_type="application/xml")
