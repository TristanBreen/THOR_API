import type { NextApiRequest, NextApiResponse } from 'next'
import { buildSummary } from '@/lib/summary'

export default function handler(_req: NextApiRequest, res: NextApiResponse) {
  try {
    res.setHeader('Cache-Control', 'no-store')
    res.status(200).json(buildSummary())
  } catch (e) {
    console.error('summary error', e)
    res.status(500).json({ error: 'Could not read the data' })
  }
}
