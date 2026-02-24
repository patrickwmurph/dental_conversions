# README 

## Data to Import Spec Mapping
Extract File Name | Import Spec |
---------|----------|
 data\DXE_Extract_ExistingTreatment.csv | res1703 |
 data\DXE_Extract_PlannedTreatment.csv | res1704 |
 data\DXE_Extract_Findings.csv | res1702 |
 data\DXE_Extract_PerioCharting.csv | res1705 |


### Column Mappings `Import Spec:Extract`
```python
plannedTreatmentMap = {
    "Patient ID"
    "Tooth VEL"
    "Inact VEL"
    "Additional Tooth VEL"
    "Encounter CSN"
    "Surfaces"
    "Procedure"
    "Comp Inst"
    "Provider"
    "Assoc Diag"
    "Comments"
    "Area of Oral Cavity"
    "Inactive For Area"
    "Exist Proc"
    "Update User"
    "Update Inst (UTC)"
    "Enc Dep"
    "Enc Prov"
    "Enc Date"
}
```

```python
existingTreatmentMap = {
"Patient ID"
"Tooth VEL"
"Inact VEL"
"Additional Tooth VEL"
"Encounter CSN"
"Surfaces"
"Procedure"
"Comp Inst"
"Provider"
"Assoc Diag"
"Comments"
"Area of Oral Cavity"
"Inactive For Area"
"Exist Proc"
"Update User"
"Update Inst (UTC)"
"Enc Dep"
"Enc Prov"
"Enc Date"
}
```
- Arch + Quadrant: These should be combined. Into one column and this will be mapped to "Area of Oral Cavity". There will never be an Arch and Quadrant documented.
- Inactive for Area: Ignore
- Exist Proc: Create a column and Set this to 0.

```python
findingsMap = {
    "Patient ID"
    "Tooth VEL
    "CSN for Perio"
    "Surfaces"
    "PARL Override Name"
    "Finding Type"
    "Associated Diagnosis"
    "Mblty Class"
    "Caries Class"
    "Caries Depth"
    "Caries Activity"
    "Caries Progression"
    "Status"
    "Caries Incipiency"
    "BL/SUP Locations"
    "Finding Cmt"
    "Furc Locations"
    "Furc Class"
    "Update User"
    "Update Inst (UTC)"
}
```

```python
perioChartingMap = {
    "Patient ID"
    "Tooth VEL"
    "Perio CSN Identifier"
    "Dental:Probing Depth"
    "Dental:Gingival Margin"
    "Dental:Perio Location"
    "Dental:Clinical Attachment Level"
    "Update User"
    "Update Inst (UTC)"
    "Enc Dep"
    "Enc Prov"
    "Enc Date"
}
```