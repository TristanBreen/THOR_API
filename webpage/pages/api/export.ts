import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<Blob | { error: string }>
) {
  try {
    // Resolve Data directory
    let dataDir = ''
    
    const possiblePaths = [
      '/home/tristan/API/API_Repoed/THOR_API/Data',
      '/data/Data',
      path.join(process.cwd(), 'Data'),
      path.join(process.cwd(), '..', 'Data'),
      path.join(process.cwd(), '../..', 'Data'),
      './Data',
    ]

    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        dataDir = p
        break
      }
    }

    if (!dataDir) {
      return res.status(500).json({ error: 'Data directory not found' })
    }

    const seizureFile = path.join(dataDir, 'seizures.csv')

    if (!fs.existsSync(seizureFile)) {
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
