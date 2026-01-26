import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<any>
) {
  try {
    // Try to find the Data directory with various paths
    let dataDir = ''
    
    // Common paths on Linux - try absolute paths first
    const absolutePaths = [
      '/home/tristan/API/API_Repoed/THOR_API/Data',
      '/home/tristan/Documents/Coding/Personal/THOR_API/THOR_API/Data',
    ]
    
    // Try absolute paths first
    for (const p of absolutePaths) {
      if (fs.existsSync(p)) {
        dataDir = p
        break
      }
    }
    
    // If not found, try relative paths from current working directory
    if (!dataDir) {
      const cwd = process.cwd()
      const relativePaths = [
        path.join(cwd, '..', 'Data'),
        path.join(cwd, '../..', 'Data'),
        path.join(cwd, '../../Data'),
        '/app/Data',
        './Data',
      ]
      
      for (const p of relativePaths) {
        if (fs.existsSync(p)) {
          dataDir = p
          break
        }
      }
    }

    if (!dataDir) {
      console.error('Data directory not found. CWD:', process.cwd())
      return res.status(500).json({ error: 'Data directory not found' })
    }

    const seizureFile = path.join(dataDir, 'seizures.csv')

    if (!fs.existsSync(seizureFile)) {
      console.error('Seizure file not found at:', seizureFile)
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
