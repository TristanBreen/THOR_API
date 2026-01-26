import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<any>
) {
  try {
    // Use the same path resolution logic as app.py
    const SERVER_BASE_PATH = '/home/tristan/API/API_Repoed/THOR_API'
    const SCRIPT_DIR = process.cwd() // In Next.js, this is the project root (webpage/)
    const PARENT_DIR = path.dirname(SCRIPT_DIR) // One level up from webpage/
    
    let BASE_DATA_DIR = ''

    // Check paths in priority order (same as app.py)
    if (fs.existsSync(path.join(SERVER_BASE_PATH, 'Data'))) {
      BASE_DATA_DIR = path.join(SERVER_BASE_PATH, 'Data')
    } else if (fs.existsSync('/data/Data')) {
      BASE_DATA_DIR = '/data/Data'
    } else if (fs.existsSync(path.join(PARENT_DIR, 'Data'))) {
      BASE_DATA_DIR = path.join(PARENT_DIR, 'Data')
    } else {
      // Fallback - still create if needed
      BASE_DATA_DIR = path.join(PARENT_DIR, 'Data')
    }

    const seizureFile = path.join(BASE_DATA_DIR, 'seizures.csv')

    console.log('[EXPORT] Using BASE_DATA_DIR:', BASE_DATA_DIR)
    console.log('[EXPORT] Looking for file:', seizureFile)
    console.log('[EXPORT] File exists:', fs.existsSync(seizureFile))

    if (!fs.existsSync(seizureFile)) {
      console.error('[EXPORT] File not found:', seizureFile)
      return res.status(404).json({ error: `File not found: ${seizureFile}` })
    }

    // Read the CSV file
    const csvContent = fs.readFileSync(seizureFile, 'utf-8')
    
    // Return as CSV file
    res.setHeader('Content-Type', 'text/csv')
    res.setHeader('Content-Disposition', 'attachment; filename="seizure_data.csv"')
    res.status(200).send(csvContent)
  } catch (error) {
    console.error('[EXPORT] Error:', error)
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Export failed',
    })
  }
}
