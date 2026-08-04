import React from 'react'
import { useTranslation } from 'react-i18next'
import { Globe } from 'lucide-react'

const LanguageSwitcher = () => {
  const { i18n } = useTranslation()

  const languages = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' }
  ]

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0]

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode)
  }

  return (
    <div className="relative group">
      <button
        className="flex items-center gap-2 px-3 py-2 text-slate-200 hover:bg-white/10 rounded-lg transition-colors"
        aria-label="Select language"
      >
        <Globe size={18} />
        <span className="text-sm font-medium">{currentLanguage.nativeName}</span>
      </button>
      
      <div className="absolute right-0 mt-1 w-36 bg-slate-950/95 rounded-lg shadow-lg border border-white/10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 backdrop-blur">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            className={`w-full px-4 py-2 text-left text-sm hover:bg-white/10 first:rounded-t-lg last:rounded-b-lg transition-colors ${
              i18n.language === lang.code
                ? 'bg-cyan-300 text-slate-950 font-bold'
                : 'text-slate-200'
            }`}
          >
            {lang.nativeName}
          </button>
        ))}
      </div>
    </div>
  )
}

export default LanguageSwitcher
