# Masseoprettelse-af-journalnotat-i-KMD-Opus-Debitor

This robot creates kundekontakter in OPUS SAP based on elements in the job queue 'Masseoprettelse-af-journalnotat-i-KMD-Opus-Debitor'.

Expected queue element:

qe.reference = fp number: string
qe.data = {
    "art": string,
    "aftaleindhold": list[string],
    "notat": string
}

## Requirements
Minimum python version 3.10

## Flow

The flow of the framework is sketched up in the following illustration:

![Flow diagram](Robot-Framework.svg)
