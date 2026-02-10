CREATE DATABASE Medipal;
USE Medipal;

CREATE TABLE Doctor(
    doctor_id VARCHAR(20) PRIMARY KEY NOT NULL,
    name VARCHAR(100),
    age INT,
    specialisation VARCHAR(100)
);
CREATE TABLE Doc_Phone_no(
    doctor_id VARCHAR(20) NOT NULL,
    phone_no CHAR(10),
    PRIMARY KEY(doctor_id,phone_no),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);

CREATE TABLE Patient(
    patient_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender CHAR(1),
    weight NUMERIC(3,2),
    blood_group VARCHAR(5)
);

CREATE TABLE Active_Ingredients (
    chemical_id VARCHAR(20) PRIMARY KEY,
    chemical_name VARCHAR(100) 
);

CREATE TABLE Manufacturer(
    manufacturer_id VARCHAR(20) PRIMARY KEY,
    street_name VARCHAR(100),
    building_name VARCHAR(100),
    house_no VARCHAR(20)
);

CREATE TABLE Manufacturer_Phone_no(
    manufacturer_id VARCHAR(20) NOT NULL,
    phone_no CHAR(10),
    PRIMARY KEY(manufacturer_id,phone_no),
    FOREIGN KEY(manufacturer_id) REFERENCES Manufacturer(manufacturer_id)
);

CREATE TABLE Drugs(
    drug_id VARCHAR(20) PRIMARY KEY,
    drug_name VARCHAR(100),
    super_drug_id VARCHAR(20),
    severity VARCHAR(50),
    FOREIGN KEY (super_drug_id) REFERENCES Drugs(drug_id)
);

CREATE TABLE Prescription(
    prescription_id VARCHAR(20) PRIMARY KEY,
    start_date DATE,
    doctor_id VARCHAR(20),
    patient_id VARCHAR(20),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
);

CREATE TABLE Contains(
    drug_id VARCHAR(20),
    chemical_id VARCHAR(20),
    PRIMARY KEY (drug_id, chemical_id),
    FOREIGN KEY (drug_id) REFERENCES Drugs(drug_id),
    FOREIGN KEY (chemical_id) REFERENCES Active_Ingredients(chemical_id)
);

CREATE TABLE Manufactures(
    manufacturer_id VARCHAR(20),
    drug_id VARCHAR(20),
    dosage VARCHAR(10),
    PRIMARY KEY (manufacturer_id, drug_id),
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
    FOREIGN KEY (drug_id) REFERENCES Drugs(drug_id)
);

CREATE TABLE Has(
    drug_id VARCHAR(20),
    prescription_id VARCHAR(20),
    PRIMARY KEY (drug_id, prescription_id),
    FOREIGN KEY (drug_id) REFERENCES Drugs(drug_id),
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id)
);

CREATE TABLE Feedback(
    feedback_no INT PRIMARY KEY,
    prescription_id VARCHAR(20),
    comments TEXT,
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id)
);


ALTER TABLE Patient MODIFY COLUMN gender CHAR(1);
ALTER TABLE Patient MODIFY COLUMN  weight NUMERIC(5,2);
ALTER TABLE Feedback MODIFY COLUMN  feedback_no VARCHAR(20);


