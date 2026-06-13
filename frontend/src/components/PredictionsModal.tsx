"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/services/api";

interface Prediction {
  username: string;
  predicted_goals1: number;
  predicted_goals2: number;
}

interface PredictionsModalProps {
  matchId: string;
  groupId: string;
  matchTitle: string;
  onClose: () => void;
}

export default function PredictionsModal({ matchId, groupId, matchTitle, onClose }: PredictionsModalProps) {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPredictions = async () => {
      try {
        const data = await apiFetch(`/groups/${groupId}/matches/${matchId}/predictions`);
        setPredictions(data);
      } catch (err) {
        console.error("Error loading group predictions", err);
      } finally {
        setLoading(false);
      }
    };
    loadPredictions();
  }, [matchId, groupId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-white w-full max-w-sm rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        <div className="bg-green-700 p-4 text-white flex justify-between items-center">
          <div>
            <h3 className="font-black text-lg leading-tight">Polla del Grupo</h3>
            <p className="text-[10px] opacity-80 uppercase tracking-widest">{matchTitle}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-full transition-colors leading-none text-2xl">×</button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center py-12 text-green-700 font-bold animate-pulse">Cargando pronósticos...</div>
          ) : predictions.length === 0 ? (
            <div className="text-center py-12 text-gray-400 font-medium italic">Nadie ha hecho pronósticos para este partido.</div>
          ) : (
            <div className="space-y-2">
              {predictions.map((p, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100">
                  <span className="font-bold text-gray-700 truncate flex-1">{p.username}</span>
                  <div className="bg-white px-4 py-1.5 rounded-xl border border-gray-200 shadow-sm font-black text-green-700 text-lg">
                    {p.predicted_goals1} - {p.predicted_goals2}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="p-4 border-t bg-gray-50">
          <button 
            onClick={onClose}
            className="w-full py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-black rounded-2xl transition-all active:scale-95"
          >
            CERRAR
          </button>
        </div>
      </div>
    </div>
  );
}
