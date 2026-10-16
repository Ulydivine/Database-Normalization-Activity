# 2NF explanation

We started from the 1NF files. Some of those tables use a composite key, and a few columns depend on only part of that key. We moved those columns out.

## Composite keys

- `project_assignments_1nf.csv`: ProjectID + WorkerPhone
- `worker_skills_1nf.csv`: ProjectID + WorkerPhone + WorkerSkill
- `worker_certifications_1nf.csv`: ProjectID + WorkerPhone + WorkerCertification
- `supplier_phones_1nf.csv`: ProjectID + SupplierName + SupplierPhone
- `materials_1nf.csv`: ProjectID + SupplierName + MaterialSupplied
- `equipment_1nf.csv`: ProjectID + SupplierName + EquipmentUsed

## Partial dependencies

In `project_assignments_1nf.csv`, the project, site, client, and supervisor columns depend only on ProjectID. WorkerName and WorkerHourlyRate depend only on WorkerPhone. SupplierName and SupplierCity need both ProjectID and WorkerPhone, so they stay on the assignment.

WorkerName on the skill and certification tables depends only on WorkerPhone.

MaterialUnitCost depends on ProjectID + MaterialSupplied, not on the supplier. Glass Panels cost 250 from both suppliers on Green Tech Campus. EquipmentRentalCost is the same kind of case. The crane on Downtown Plaza is 5000 from both suppliers.

`supplier_phones_1nf.csv` has no column outside its key, so it did not need a split.

## Tables we made

- `project.csv` has the project, site, client, and supervisor columns. Primary key: ProjectID.
- `worker.csv` has WorkerPhone, WorkerName, and WorkerHourlyRate. Primary key: WorkerPhone.
- `project_worker.csv` has ProjectID, WorkerPhone, SupplierName, and SupplierCity. Primary key: ProjectID + WorkerPhone. ProjectID references project. WorkerPhone references worker.
- `worker_skill.csv` and `worker_certification.csv` drop WorkerName. Their keys are ProjectID + WorkerPhone + the skill or certification, and that pair references project_worker.
- `supplier_phone.csv` is unchanged from 1NF. Primary key: ProjectID + SupplierName + SupplierPhone.
- `material_cost.csv` stores the unit cost. Primary key: ProjectID + MaterialSupplied. `project_supplier_material.csv` links the supplier to that material.
- `equipment_cost.csv` stores the rental cost. Primary key: ProjectID + EquipmentUsed. `project_supplier_equipment.csv` links the supplier to that equipment.

## Why this is 2NF

Every cell still has one value, and non-key columns now depend on the whole key. Client details, supervisor details, and supplier city are still repeated. Those are not partial dependencies, so we left them for the next stage.
