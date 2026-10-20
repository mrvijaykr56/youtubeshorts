import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function RenderStepper({ progressText, progressPercent, pipelineSteps, activeStepIdx }) {
  return (
    <div className="space-y-8 py-6 overflow-hidden">
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="relative">
          <div className="absolute inset-0 bg-indigo-500/20 rounded-full blur-xl animate-pulse" />
          <Loader2 className="w-14 h-14 text-indigo-400 animate-spin relative" />
        </div>
        <h3 className="text-lg font-bold text-white tracking-wide">Rendering Your Masterpiece</h3>
        <p className="text-indigo-300 font-medium text-sm animate-pulse bg-indigo-500/10 px-4 py-1.5 rounded-full border border-indigo-500/25">
          {progressText}
        </p>
      </div>

      {/* Glowing Premium Progress Bar */}
      <div className="w-full max-w-md mx-auto space-y-2">
        <div className="flex justify-between items-center text-xs text-gray-400 tracking-wider">
          <span className="font-semibold uppercase">Overall Progress</span>
          <span className="text-indigo-400 font-extrabold bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-500/20">
            {progressPercent}%
          </span>
        </div>
        <div className="w-full h-3 bg-gray-950 rounded-full p-0.5 border border-gray-800 overflow-hidden relative shadow-inner">
          <motion.div 
            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full shadow-[0_0_12px_rgba(99,102,241,0.5)]" 
            initial={{ width: '0%' }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Stepper Timeline Visualizer */}
      <div className="relative pt-4 max-w-lg mx-auto">
        <div className="absolute top-[28px] left-6 right-6 h-1.5 bg-gray-950 rounded-full" />
        <motion.div 
          className="absolute top-[28px] left-6 h-1.5 bg-gradient-to-r from-indigo-500 to-indigo-400 rounded-full" 
          initial={{ width: '0%' }}
          animate={{ width: `${(activeStepIdx / (pipelineSteps.length - 1)) * 100}%` }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
        
        <div className="relative flex justify-between">
          {pipelineSteps.map((step, idx) => {
            const isCompleted = idx < activeStepIdx;
            const isActive = idx === activeStepIdx;
            return (
              <motion.div 
                key={idx} 
                animate={isActive ? { scale: 1.08 } : { scale: 1 }}
                className="flex flex-col items-center group relative"
              >
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-xs z-10 transition-all ${
                  isCompleted 
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/30'
                    : isActive
                      ? 'bg-gray-950 border-indigo-400 text-indigo-400 ring-4 ring-indigo-500/25 scale-110'
                      : 'bg-gray-950 border-gray-800 text-gray-500'
                }`}>
                  {isCompleted ? '✓' : idx + 1}
                </div>
                <div className="mt-2 text-center">
                  <h4 className={`text-[10px] font-bold tracking-wider uppercase ${isActive ? 'text-indigo-400' : 'text-gray-400'}`}>{step.name}</h4>
                  <p className="text-[8px] text-gray-500 mt-0.5 max-w-[70px] leading-tight hidden sm:block">{step.desc}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
