import { Sparkles } from 'lucide-react';

export default function ScriptInput({ script, setScript, disabled }) {
  return (
    <div>
      <label htmlFor="script" className="block text-sm font-semibold tracking-wider text-gray-300 uppercase flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-indigo-400" /> Input Script
      </label>
      <div className="mt-2">
        <textarea
          id="script"
          rows={5}
          className="block w-full rounded-2xl border-0 bg-gray-950 py-4 px-5 text-white shadow-sm ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-indigo-500 sm:text-sm sm:leading-6 transition-all placeholder-gray-600"
          placeholder="E.g., Ever wonder what happens if you drop a bowling ball in space? Let's check out the mind-bending reality..."
          value={script}
          onChange={(e) => setScript(e.target.value)}
          disabled={disabled}
        />
      </div>
    </div>
  );
}
