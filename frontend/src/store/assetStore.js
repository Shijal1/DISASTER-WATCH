
import { create } from 'zustand'
import { listAssets } from '../api/assets.js'

export const useAssetStore = create((set) => ({
  assets: [],
  async refresh() {
    const assets = await listAssets()
    set({ assets })
  },
}))
