import { useEffect, useState } from 'react'
import { WMSTileLayer } from 'react-leaflet'

const INSTANCE_ID = '4877e93a-6038-4e52-ba18-ee81f2174f1d'
const WMS_URL = `https://sh.dataspace.copernicus.eu/ogc/wms/${INSTANCE_ID}`

const LAYER_MAP = {
  TRUE_COLOR: 'TRUE-COLOR-S2L2A',
  NDWI: 'NDWI',
  NBR: 'NDWI',
}

export default function SatelliteOverlay({ layer, opacity = 0.7 }) {
  const [token, setToken] = useState(null)

  useEffect(() => {
    fetch('/api/satellite/token')
      .then(r => r.json())
      .then(d => setToken(d.access_token))
      .catch(() => setToken(null))
  }, [])

  if (!token || !layer) return null

  const layerName = LAYER_MAP[layer] || layer

  return (
    <WMSTileLayer
      url={WMS_URL}
      layers={layerName}
      format="image/png"
      transparent={true}
      version="1.1.1"
      opacity={opacity}
      params={{ access_token: token }}
    />
  )
}