# First Normal Form (1NF)

This explanation covers 1NF only. The original file is `construction_projects.csv`: 15 rows, 26 columns, and 7 projects (P001–P007).

## Entities and their columns

| Entity | Columns |
| --- | --- |
| Project | ProjectID, ProjectName, ProjectType, StartDate, EndDate, SiteAddress, SiteCity, SiteState |
| Client | ClientName, ClientPhone, ClientEmail, ClientCity |
| Supervisor | SupervisorName, SupervisorPhone |
| Worker | WorkerName, WorkerPhone, WorkerHourlyRate |
| Supplier | SupplierName, SupplierCity, SupplierPhones |
| Material | MaterialSupplied, MaterialUnitCost |
| Equipment | EquipmentUsed, EquipmentRentalCost |

`WorkerSkills` and `WorkerCertifications` describe a worker on a particular project. The same worker has different skills on different projects.

## Columns repeated on many rows

Project name, dates, site, client, and supervisor are copied onto every worker row of that project. Supplier city is copied for the same supplier. Worker name and hourly rate are copied for the same worker. Example: P001 is stored three times, once for Mike Ross, Rachel Zane, and Harvey Specter.

## Columns that violated 1NF

These cells contain more than one value, separated by `|`.

| Column | Example from P001, Mike Ross, BuildPro Supplies |
| --- | --- |
| WorkerSkills | Carpentry\|Framing |
| WorkerCertifications | OSHA\|First Aid |
| SupplierPhones | 617-555-9000\|617-555-9001 |
| MaterialSupplied | Concrete\|Steel |
| MaterialUnitCost | 120\|300 |
| EquipmentUsed | Crane\|Bulldozer |
| EquipmentRentalCost | 5000\|3000 |

Skills and certifications are two separate lists. The first material cost belongs to the first material: Concrete costs 120 and Steel costs 300. Equipment works the same way: Crane costs 5000 and Bulldozer costs 3000.

A space is part of one value. `New York`, `San Diego`, `Steel Beams`, and `First Aid` were not split.

## How the values were made atomic

Both new rows and new tables were created. Each `|` list became one row per value.

| File | Rows | Primary key | Link back |
| --- | --- | --- | --- |
| `project_assignments_1nf.csv` | 15 | (ProjectID, WorkerPhone) | One original row, with the list columns removed |
| `worker_skills_1nf.csv` | 30 | (ProjectID, WorkerPhone, WorkerSkill) | Foreign key (ProjectID, WorkerPhone) to assignments |
| `worker_certifications_1nf.csv` | 30 | (ProjectID, WorkerPhone, WorkerCertification) | Foreign key (ProjectID, WorkerPhone) to assignments |
| `supplier_phones_1nf.csv` | 15 | (ProjectID, SupplierName, SupplierPhone) | Matches assignments on ProjectID and SupplierName |
| `materials_1nf.csv` | 16 | (ProjectID, SupplierName, MaterialSupplied) | Matches assignments on ProjectID and SupplierName |
| `equipment_1nf.csv` | 16 | (ProjectID, SupplierName, EquipmentUsed) | Matches assignments on ProjectID and SupplierName |

`ProjectID` alone is not a key, because P001 has three rows. `WorkerPhone` alone is not a key, because Mike Ross (`617-555-3001`) is on four projects. Together they identify each assignment row. No new ID numbers were added.

Phones, materials, and equipment are stored once per project and supplier. On P001, Mike Ross and Rachel Zane both list the same BuildPro phones, materials, and equipment. Each assignment row still names the supplier. `(ProjectID, SupplierName)` is the join for those three files. It is not the primary key of the assignment table.

## Relationships

- One client has many projects, and each project has one client. Metro Corp has P001 and P005.
- One supervisor has many projects, and each project has one supervisor.
- Projects and workers are many-to-many. P001 has three workers, and Mike Ross is on four projects.
- Projects and suppliers are many-to-many. P004 has two suppliers, and BuildPro Supplies is on P001 and P003.
- One worker on one project has many skills and many certifications.
- One supplier on one project has many phones, many materials, and many equipment items.

## Dependencies found in the data

These dependencies are recorded here and were left in place. Removing them belongs to the later stages.

- ProjectID determines the project name, type, dates, site, client, and supervisor.
- ClientName determines the client phone, email, and city.
- SupervisorName determines the supervisor phone.
- WorkerPhone determines the worker name. In this file it also determines the hourly rate.
- SupplierName determines the supplier city.
- (ProjectID, SupplierName, MaterialSupplied) determines the unit cost.
- (ProjectID, SupplierName, EquipmentUsed) determines the rental cost.
- A skill or certification depends on both the project and the worker. Mike Ross has Carpentry and Framing on P001, and Carpentry and Concrete on P002.

## Why this is 1NF

- Every cell now holds one value.
- The `|` repeating groups are separate rows.
- Every row can be identified by the key in the table above. Those keys were checked and are unique.