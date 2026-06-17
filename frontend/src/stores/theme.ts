import { writable } from 'svelte/store'

export type ThemeName =
  | 'light'
  | 'dark'
  | 'cupcake'
  | 'retro'
  | 'synthwave'
  | 'forest'
  | 'coffee'
  | 'abyss'
  | 'sunset'

export interface ThemeOption {
  name: ThemeName
  label: string
  isDark: boolean
  primary: string
  secondary: string
  accent: string
  neutral: string
  background: string
  text: string
}

export const themes: ThemeOption[] = [
  { name: 'light', label: '라이트', isDark: false, primary: '#4f46e5', secondary: '#ec4899', accent: '#f59e0b', neutral: '#1f2937', background: '#ffffff', text: '#1f2937' },
  { name: 'dark', label: '다크', isDark: true, primary: '#6366f1', secondary: '#d946ef', accent: '#14b8a6', neutral: '#191d24', background: '#1d232a', text: '#a6adbb' },
  { name: 'cupcake', label: '컵케이크', isDark: false, primary: '#65c3c8', secondary: '#ef9fbc', accent: '#eeaf3a', neutral: '#291334', background: '#faf7f5', text: '#291334' },
  { name: 'retro', label: '레트로', isDark: false, primary: '#ef9995', secondary: '#a4cbb4', accent: '#ebdc99', neutral: '#282425', background: '#ece3ca', text: '#282425' },
  { name: 'synthwave', label: '신스웨이브', isDark: true, primary: '#e779c1', secondary: '#86edac', accent: '#f3e895', neutral: '#190e2f', background: '#1a103c', text: '#a6adbb' },
  { name: 'forest', label: '포레스트', isDark: true, primary: '#1eb854', secondary: '#12b886', accent: '#1f2937', neutral: '#110e0e', background: '#171212', text: '#a6adbb' },
  { name: 'coffee', label: '커피', isDark: true, primary: '#db924b', secondary: '#263e3f', accent: '#1c1917', neutral: '#11090f', background: '#20161f', text: '#a6adbb' },
  { name: 'abyss', label: '어비스', isDark: true, primary: '#3b82f6', secondary: '#06b6d4', accent: '#1e1b4b', neutral: '#111827', background: '#0f172a', text: '#a6adbb' },
  { name: 'sunset', label: '선셋', isDark: true, primary: '#ff865b', secondary: '#fd6f9c', accent: '#8a5cf5', neutral: '#160e1b', background: '#120e16', text: '#a6adbb' },
]

const STORAGE_KEY = 'yt-dlp-webui-theme'

function getInitialTheme(): ThemeName {
  if (typeof window === 'undefined') return 'light'

  const saved = localStorage.getItem(STORAGE_KEY) as ThemeName | null
  if (saved && themes.some((t) => t.name === saved)) {
    return saved
  }

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  return prefersDark ? 'dark' : 'light'
}

export const activeTheme = writable<ThemeName>(getInitialTheme())

if (typeof window !== 'undefined') {
  activeTheme.subscribe((theme) => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(STORAGE_KEY, theme)
  })
}
