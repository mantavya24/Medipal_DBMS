USE Medipal;
SHOW TABLES;

Insert Into DOCTOR Values('doc001','Ramesh Kumar',54,'Cardiologist');
Insert Into DOCTOR Values('doc002','Sukrit Dang',44,'Neurologist');
Insert Into DOCTOR Values('doc003','Avni Yadav',36,'Dermatologist');
Insert Into DOCTOR Values('doc004','Aryav Jain',42,'Pediatrician');
Insert Into DOCTOR Values('doc005','Mantavya Arun Kumar',32,'Cardiologist');
Insert Into DOCTOR Values('doc006','Arnav Ranjan',43,'Oncologist');
Insert Into DOCTOR Values('doc007','Bhavya Joshi',45,'Oncologist');
Insert Into DOCTOR Values('doc008','Soumya Singh',75,'Gastroenterologist');
Insert Into DOCTOR Values('doc009','Ishaan Dhull',74,'Pediatrician');
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


INSERT INTO Manufacturer VALUES ('m001','Churchgate','Eros Build','42');
INSERT INTO Manufacturer VALUES ('m002','Hazratganj', 'Lucknow Plaza','15/9');
INSERT INTO Manufacturer VALUES ('m003','Bani Park', 'Jaipur Heritage', 'S-21');
INSERT INTO Manufacturer VALUES ('m004','Salt Lake Sector V', 'Techno Park', 'Block-EP');
INSERT INTO Manufacturer VALUES ('m005','Koramangala 80ft Rd', 'Indus View', '777');
INSERT INTO Manufacturer Values ('m006','Connaught Place', 'Statesman House', 'B-14');
INSERT INTO Manufacturer VALUES ('m007','Hitech City', 'Cyber Gateway', 'Phase-II');
INSERT INTO Manufacturer VALUES ('m008','FC Road', 'Deccan Heights', '1092');
INSERT INTO Manufacturer VALUES ('m009','T-Nagar', 'Chennai Hub', '88-C');
INSERT INTO Manufacturer VALUES ('m010','Race Course Rd', 'Royal Enclave','10');
USE Medipal;
INSERT INTO Manufacturer (manufacturer_id, street_name, building_name, house_no) VALUES 
('m011','Park Street','Apeejay House','15'),
('m012','Indiranagar100ft','Metro Tower','402'),
('m013','Gomti Nagar','Summit Plaza','C-12'),
('m014','Bandra Kurla Complex', 'Trade Centre','G-Block'),
('m015','MG Road','Cauvery Bhavan','Floor 5'),
('m016','Sector 17','Chandigarh Hub','Sco-24'),
('m017','Viman Nagar','Phoenix Market City','W-10'),
('m018','Jubilee Hills','Road No 36 Plaza','7/B'),
('m019','Marine Drive','Sea Face View','99'),
('m020','Salt Lake Sector','Kolkata IT Park','Module 4');

INSERT INTO Prescription VALUES ('pre001', '2026-01-10', 'doc001', 'pat001');
INSERT INTO Prescription VALUES ('pre002', '2026-01-12', 'doc002', 'pat002');
INSERT INTO Prescription VALUES ('pre003', '2026-01-15', 'doc003', 'pat003');
INSERT INTO Prescription VALUES ('pre004', '2026-01-18', 'doc004', 'pat004');
INSERT INTO Prescription VALUES ('pre005', '2026-01-20', 'doc005', 'pat005');
INSERT INTO Prescription VALUES ('pre006', '2026-01-22', 'doc006', 'pat006');
INSERT INTO Prescription VALUES ('pre007', '2026-01-25', 'doc007', 'pat007');
INSERT INTO Prescription VALUES ('pre008', '2026-01-28', 'doc008', 'pat008');
INSERT INTO Prescription VALUES ('pre009', '2026-02-01', 'doc009', 'pat010');
INSERT INTO Prescription VALUES ('pre010', '2026-02-05', 'doc010', 'pat011');
INSERT INTO Prescription VALUES ('pre011', '2026-02-23', 'doc005', 'pat005');
INSERT INTO Prescription VALUES ('pre012', '2026-04-12', 'doc008', 'pat008');
INSERT INTO Prescription VALUES ('pre013', '2026-05-01', 'doc002', 'pat002');
INSERT INTO Prescription VALUES ('pre014', '2026-06-13', 'doc004', 'pat004');
INSERT INTO Prescription VALUES ('pre015', '2026-06-21', 'doc007', 'pat007');
INSERT INTO Prescription VALUES ('pre016', '2026-06-23', 'doc006', 'pat006');
INSERT INTO Prescription VALUES ('pre017', '2026-04-12', 'doc003', 'pat003');
INSERT INTO Prescription VALUES ('pre018', '2026-03-11', 'doc002', 'pat002');
INSERT INTO Prescription VALUES ('pre019', '2026-02-09', 'doc001', 'pat001');
INSERT INTO Prescription VALUES ('pre020', '2026-01-07', 'doc009', 'pat010');


INSERT INTO Feedback (feedback_no, prescription_id, comments) VALUES 
('f001', 'pre001', 'Patient reported significant improvement in chest pain.'),
('f002', 'pre002', 'Headaches have reduced, but patient feels slightly drowsy.'),
('f003', 'pre003', 'Skin rash has cleared up completely after one week.'),
('f004', 'pre004', 'Patient is responding well to the pediatric dosage.'),
('f005', 'pre005', 'Joint pain is still present; may need to review dosage.'),
('f006', 'pre006', 'Patient feels much more stable emotionally.'),
('f007', 'pre007', 'Nausea reported after taking the morning dose.'),
('f008', 'pre008', 'Digestion has improved significantly.'),
('f009', 'pre009', 'Hormone levels are stabilizing as per latest tests.'),
('f010', 'pre010', 'Vision clarity has improved; no irritation noted.'),
('f011', 'pre011', 'Follow-up: Recovery is on track, patient back to light exercise.'),
('f012', 'pre012', 'Patient requested a refill; symptoms under control.'),
('f013', 'pre013', 'Occasional dizziness noted in the evenings.'),
('f014', 'pre014', 'Child is much more active and fever has not returned.'),
('f015', 'pre015', 'Treatment completed; patient is now asymptomatic.');

USE Medipal;

INSERT INTO Drugs(drug_id, drug_name, super_drug_id, severity)VALUES 
('dr001','Aspirin',NULL,NULL),
('dr002','Warfarin','dr001','High'),
('dr003', 'Metformin', NULL,NULL),
('dr004','Lisinopril', NULL, 'Medium'),
('dr005','Potassium Chloride','dr004','High'),
('dr006','Amoxicillin', NULL,NULL),
('dr007','Methotrexate','dr001','High'),
('dr008', 'Atorvastatin', NULL,NULL),
('dr009','Clarithromycin','dr008','High'),
('dr010','Albuterol', NULL,NULL),
('dr011','Propranolol', 'dr010', 'Medium'),
('dr012','Omeprazole',NULL,NULL),
('dr013','Clopidogrel', 'dr012', 'Medium'),
('dr014','Levothyroxine', NULL,NULL),
('dr015','Calcium Carbonate', 'dr014', 'Low'),
('dr016','Sertraline', NULL,NULL),
('dr017','Tramadol', 'dr016', 'High'),
('dr018','Amlodipine', NULL,NULL),
('dr019','Simvastatin', 'dr009', 'High'),
('dr020','Ibuprofen', 'dr001', 'Medium');




INSERT INTO Active_Ingredients (chemical_id, chemical_name) VALUES 
('ch001','Acetylsalicylic Acid'),
('ch002','Warfarin Sodium'),
('ch003','Metformin Hydrochloride'),
('ch004','Lisinopril Dihydrate'),
('ch005','Potassium Chloride'),
('ch006','Amoxicillin Trihydrate'),
('ch007','Methotrexate Sodium'),
('ch008','Atorvastatin Calcium'),
('ch009','Clarithromycin'),
('ch010','Albuterol Sulfate'),
('ch011','Propranolol Hydrochloride'),
('ch012','Omeprazole Magnesium'),
('ch013','Clopidogrel Bisulfate'),
('ch014','Levothyroxine Sodium'),
('ch015','Calcium Carbonate'),
('ch016','Sertraline Hydrochloride'),
('ch017','Tramadol Hydrochloride'),
('ch018','Amlodipine Besylate'),
('ch019','Simvastatin'),
('ch020','Ibuprofen');

USE Medipal;

INSERT INTO Contains (drug_id, chemical_id) VALUES 
('dr001', 'ch001'),
('dr002', 'ch002'),
('dr003', 'ch003'),
('dr004', 'ch004'),
('dr005', 'ch005'),
('dr006', 'ch006'),
('dr007', 'ch007'),
('dr008', 'ch008'),
('dr009', 'ch009'),
('dr010', 'ch010'),
('dr011', 'ch011'),
('dr012', 'ch012'),
('dr013', 'ch013'),
('dr014', 'ch014'),
('dr015', 'ch015'),
('dr017', 'ch017'),
('dr018', 'ch018'),
('dr019', 'ch019'),
('dr020', 'ch020');
Insert into Contains values('dr016', 'ch016');


USE Medipal;
INSERT INTO Manufactures (manufacturer_id,drug_id,dosage) VALUES 
('m001','dr001','100mg'),
('m002','dr002','50mg'),
('m003','dr003','100mg'),
('m004','dr004','50mg'),
('m005','dr005','100mg'),
('m006','dr006','50mg'),
('m007','dr007','100mg'),
('m008','dr008','50mg'),
('m009','dr009','100mg'),
('m010','dr010','50mg'),
('m011','dr011','100mg'),
('m012','dr012','50mg'),
('m013','dr013','100mg'),
('m014','dr014','50mg'),
('m015','dr015','50mg'),
('m016','dr016','100mg'),
('m017','dr017','50mg'),
('m018','dr018','100mg'),
('m019','dr019','50mg'),
('m020','dr020','100mg');

USE Medipal;
INSERT INTO Has(drug_id,prescription_id) VALUES 
('dr001','pre001'),
('dr002','pre002'),
('dr003','pre003'),
('dr004','pre004'),
('dr005','pre005'),
('dr006','pre007'),
('dr007','pre008'),
('dr008','pre009'),
('dr009','pre010'),
('dr010','pre011'),
('dr011','pre012'),
('dr012','pre013'),
('dr013','pre014'),
('dr014','pre015'),
('dr015','pre016'),
('dr017','pre017'),
('dr018','pre018'),
('dr019','pre019'),
('dr020','pre020');


INSERT INTO Has(drug_id,prescription_id) VALUES 
('dr001','pre001'),
('dr002','pre002'),
('dr003','pre003'),
('dr004','pre004'),
('dr005','pre005'),
('dr006','pre007'),
('dr007','pre008'),
('dr008','pre009'),
('dr009','pre010'),
('dr010','pre011'),
('dr011','pre012'),
('dr012','pre013'),
('dr013','pre014'),
('dr014','pre015'),
('dr015','pre016'),
('dr017','pre017'),
('dr018','pre018'),
('dr019','pre019'),
('dr020','pre020');


INSERT INTO Has(drug_id,prescription_id) VALUES 
('dr001','pre001'),
('dr002','pre002'),
('dr003','pre003'),
('dr004','pre004'),
('dr005','pre005'),
('dr006','pre007'),
('dr007','pre008'),
('dr008','pre009'),
('dr009','pre010'),
('dr010','pre011'),
('dr011','pre012'),
('dr012','pre013'),
('dr013','pre014'),
('dr014','pre015'),
('dr015','pre016'),
('dr017','pre017'),
('dr018','pre018'),
('dr019','pre019'),
('dr020','pre020');

USE Medipal;
INSERT INTO Doc_Phone_no(doctor_id,phone_no) VALUES 
('doc001','9811771298'),
('doc001','9876543210'),
('doc002','9123456789'),
('doc003','8826110022'),
('doc004','7733044556'),
('doc005','9988776655'),
('doc005','8123498765'),
('doc006','7012345678'),
('doc007','6309876543'),
('doc008','9500123456'),
('doc009','8245611223'),
('doc010','9444012345'),
('doc011','8012344556');

USE Medipal;
INSERT INTO Manufacturer_Phone_no(manufacturer_id,phone_no) VALUES 
('m001','9811771298'),
('m001','9876543210'),
('m002','9123456789'),
('m003','8826110022'),
('m004','7733044556'),
('m005','9988776655'),
('m005','8123498765'),
('m006','7012345678'),
('m007','6309876543'),
('m008','9500123456'),
('m009','8245611223'),
('m010','9444012345'),
('m011','8012344556'),
('m012','9123400987'),
('m013','8223344556'),
('m014','7665544332'),
('m015','9810022334'),
('m016','6390122334'),
('m017','8877665544'),
('m018','7443322110'),
('m019','9550011223'),
('m020','8009988776');
