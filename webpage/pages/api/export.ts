import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<any>
) {
  try {
    // Resolve Data directory
    let dataDir = ''
    
    const possiblePaths = [
      // Production paths
      '/home/tristan/API/API_Repoed/THOR_API/Data',
      '/data/Data',
      // Development - from webpage root, go up to THOR_API
      path.join(process.cwd(), '..', 'Data'),
      path.join(process.cwd(), '../..', 'Data'),
      path.join(__dirname, '../../Data'),
      path.join(__dirname, '../../../Data'),
      './Data',
    ]

    console.log('Searching for Data directory. Current working directory:', process.cwd())
    
    for (const p of possiblePaths) {
      console.log('Checking path:', p, 'exists:', fs.existsSync(p))
      if (fs.existsSync(p)) {
        dataDir = p
        console.log('Found data directory:', dataDir)
        break
      }
    }

    if (!dataDir) {
      console.error('Data directory not found. Tried paths:', possiblePaths)
      return res.status(500).json({ error: 'Data directory not found' })
    }

    const seizureFile = path.join(dataDir, 'seizures.csv')

    if (!fs.existsSync(seizureFile)) {
      console.error('Seizure file not found:', seizureFile)
      return res.status(404).json({ error: 'Seizure data file not found' })
    }

    // Read the CSV file
    const csvContent = fs.readFileSync(seizureFile, 'utf-8')
    
    // Return as CSV file
    res.setHeader('Content-Type', 'text/csv')
    res.setHeader('Content-Disposition', 'attachment; filename="seizure_data.csv"')
    res.status(200).send(csvContent)
  } catch (error) {
    console.error('Export error:', error)
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Export failed',
    })
  }
}
