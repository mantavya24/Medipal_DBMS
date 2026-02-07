USE Medipal;
SHOW TABLES;

ALTER TABLE Patient MODIFY COLUMN gender CHAR(1);
ALTER TABLE Patient MODIFY COLUMN  weight NUMERIC(5,2);

Insert Into DOCTOR Values('doc001','Ramesh Kumar',54,'Cardiologist');
Insert Into DOCTOR Values('doc002','Sukrit Dang',44,'Neurologist');
Insert Into DOCTOR Values('doc003','Avni Yadav',36,'Dermatologist');
Insert Into DOCTOR Values('doc004','Aryav Jain',42,'Pediatrician');
Insert Into DOCTOR Values('doc005','Mantavya Arun Kumar',32,'Cardiologist');
Insert Into DOCTOR Values('doc006','Arnav Ranjan',43,'Oncologist');
Insert Into DOCTOR Values('doc007','Bhavya Joshi',45,'Oncologist');
Insert Into DOCTOR Values('doc008','Soumya Singh',75,'Gastroenterologist');
Insert Into DOCTOR Values('doc010','Eshaan Garg',64,'Endocrinologist');
Insert Into DOCTOR Values('doc011','Vihaan Sharma',44,'Endocrinologist');



Insert Into Patient Values('pat001','Aarav Sharma',24,'M',88.32,'O+');
Insert Into Patient Values('pat002','Ananya Iyer',14,'F',54.43,'B+');
Insert Into Patient Values('pat003','Ishaan Malhotra',18,'M',54.32,'AB-');
Insert Into Patient Values('pat004','Arjun Nair',21,'M',32.54,'A-');
Insert Into Patient Values('pat005','Kyra Kapoor',26,'F',87.65,'B-');
Insert Into Patient Values('pat006','Rohan Das',37,'M',65.54,'AB');
Insert Into Patient Values('pat007','Meera Verma',86,'F',53.45,'O-');
Insert Into Patient Values('pat008','Vihaan Gupta',32,'M',54.00,'O+');
Insert Into Patient Values('pat010','Diya Reddy',11,'F',98.99,'B-');
Insert Into Patient Values('pat011','Saanvi Joshi',34,'F',76.54,'AB+');


INSERT INTO Active_Ingredients (chemical_id, chemical_name) VALUES
('C001', 'Sildenafil'),           -- Found in Viagra
('C002', 'Isosorbide Mononitrate'),-- Found in Monotrate (Heart medicine)
('C003', 'Warfarin'),             -- Blood thinner
('C004', 'Aspirin'),              -- Pain/Blood thinner
('C005', 'Metformin'),            -- Diabetes
('C006', 'Lisinopril'),           -- Blood pressure
('C007', 'Atorvastatin'),         -- Cholesterol
('C008', 'Amoxicillin'),          -- Antibiotic
('C009', 'Alprazolam'),           -- Anxiety
('C010', 'Omeprazole');           -- Antacid


-- Mapping common brand names and assigning initial severity levels
-- Logic: super_drug_id is used for brand/generic hierarchy as per your schema
INSERT INTO Drugs (drug_id, drug_name, super_drug_id, severity) VALUES
('DR001', 'Viagra', NULL, 'High'),
('DR002', 'Monotrate', NULL, 'High'),
('DR003', 'Coumadin', 'DR004', 'Moderate'), -- Warfarin brand
('DR004', 'Warfarin-Generic', NULL, 'Moderate'),
('DR005', 'Ecosprin', NULL, 'Low'),         -- Aspirin brand
('DR006', 'Glucophage', NULL, 'Moderate'),   -- Metformin brand
('DR007', 'Zestril', NULL, 'Moderate'),      -- Lisinopril brand
('DR008', 'Lipitor', NULL, 'Low'),          -- Atorvastatin brand
('DR009', 'Xanax', NULL, 'High'),           -- Alprazolam brand
('DR010', 'Prilosec', NULL, 'Low');         -- Omeprazole brand

-- MAPPING DRUGS TO INGREDIENTS (CONTAINS TABLE)
INSERT INTO Contains (drug_id, chemical_id) VALUES
('DR001', 'C001'), ('DR002', 'C002'), 
('DR003', 'C003'), ('DR004', 'C003'),
('DR005', 'C004'), ('DR006', 'C005'),
('DR007', 'C006'), ('DR008', 'C007'),
('DR009', 'C009'), ('DR010', 'C010');
