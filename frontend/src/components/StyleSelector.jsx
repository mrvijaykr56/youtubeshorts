import { motion } from 'framer-motion';

export default function StyleSelector({ artStyle, setArtStyle, artStyles }) {
  return (
    <div className="space-y-3 pt-2">
      <label className="block text-sm font-semibold tracking-wider text-gray-300 uppercase">
        🎬 Background Art Style Preset
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {artStyles.map((style) => (
          <motion.button
            key={style.id}
            type="button"
            onClick={() => setArtStyle(style.id)}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.97 }}
            className={`flex flex-col items-center justify-between p-4 rounded-2xl border transition-all text-center relative overflow-hidden group cursor-pointer ${
              artStyle === style.id
                ? 'border-indigo-500 bg-indigo-950/30 shadow-lg shadow-indigo-500/10'
                : 'border-gray-800 bg-gray-950/40 hover:border-gray-700 hover:bg-gray-950/70'
            }`}
          >
            <div className={`absolute top-0 inset-x-0 h-1 bg-gradient-to-r ${style.gradient} opacity-80`} />
            <span className="text-3xl my-2 group-hover:scale-110 transition-transform">{style.icon}</span>
            <div>
              <h4 className="font-bold text-xs text-white uppercase tracking-wider">{style.name}</h4>
              <p className="text-[10px] text-gray-500 mt-1 leading-tight">{style.description}</p>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
