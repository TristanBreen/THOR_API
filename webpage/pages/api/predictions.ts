import { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Use the same path resolution logic as export.ts
    const SERVER_BASE_PATH = '/home/tristan/API/API_Repoed/THOR_API'
    const SCRIPT_DIR = process.cwd()
    const PARENT_DIR = path.dirname(SCRIPT_DIR)
    
    let BASE_DATA_DIR = ''

    // Check paths in priority order
    if (fs.existsSync(path.join(SERVER_BASE_PATH, 'Data'))) {
      BASE_DATA_DIR = path.join(SERVER_BASE_PATH, 'Data')
    } else if (fs.existsSync('/data/Data')) {
      BASE_DATA_DIR = '/data/Data'
    } else if (fs.existsSync(path.join(PARENT_DIR, 'Data'))) {
      BASE_DATA_DIR = path.join(PARENT_DIR, 'Data')
    } else {
      BASE_DATA_DIR = path.join(PARENT_DIR, 'Data')
    }

    const predictionPath = path.join(BASE_DATA_DIR, 'prediction.txt')
    const content = fs.readFileSync(predictionPath, 'utf-8')

    // Parse the prediction data
    const lines = content.trim().split('\n')
    
    let pred24 = 0
    let pred48 = 0
    let pred72 = 0

    // Extract percentages from each line
    lines.forEach((line) => {
      if (line.includes('24 hours')) {
        const match = line.match(/(\d+\.?\d*)%/)
        if (match) pred24 = parseFloat(match[1])
      } else if (line.includes('48 hours')) {
        const match = line.match(/(\d+\.?\d*)%/)
        if (match) pred48 = parseFloat(match[1])
      } else if (line.includes('72 hours')) {
        const match = line.match(/(\d+\.?\d*)%/)
        if (match) pred72 = parseFloat(match[1])
      }
    })

    res.status(200).json({
      pred24,
      pred48,
      pred72,
    })
  } catch (error) {
    console.error('Error reading prediction file:', error)
    res.status(500).json({
      error: 'Failed to read predictions',
      pred24: 0,
      pred48: 0,
      pred72: 0,
    })
  }
}
