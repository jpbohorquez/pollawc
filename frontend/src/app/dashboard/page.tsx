"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";

interface Match {
  id: string;
  team1: string;
  team2: string;
  start_at: string;
  group_name: string;
  phase: string;
}

interface PredictionState {
  [key: string]: {
    goals1: string;
    goals2: string;
  };
}

export default function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [predictions, setPredictions] = useState<PredictionState>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const data = await apiFetch("/matches");
        // Ordenar por fecha
        const sorted = data.sort((a: Match, b: Match) => 
          new Date(a.start_at).getTime() - new Date(b.start_at).getTime()
        );
        setMatches(sorted);
        
        // Inicializar estado de predicciones
        const initialPreds: PredictionState = {};
        data.forEach((m: Match) => {
          initialPreds[m.id] = { goals1: "", goals2: "" };
        });
        setPredictions(initialPreds);
      } catch (err) {
        console.error("Error fetching matches", err);
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    fetchMatches();
  }, [router]);

  const handleInputChange = (matchId: string, team: 1 | 2, value: string) => {
    setPredictions(prev => ({
      ...prev,
      [matchId]: {
        ...prev[matchId],
        [`goals${team}`]: value
      }
    }));
  };

  const isLocked = (startAt: string) => {
    const matchTime = new Date(startAt).getTime();
    const now = new Date().getTime();
    const diffMinutes = (matchTime - now) / (1000 * 60);
    return diffMinutes < 5;
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      // Filtrar solo las que tienen datos y no están bloqueadas
      const toSave = Object.entries(predictions)
        .filter(([id, data]) => {
          const match = matches.find(m => m.id === id);
          return data.goals1 !== "" && data.goals2 !== "" && match && !isLocked(match.start_at);
        })
        .map(([id, data]) => ({
          match_id: id,
          predicted_goals1: parseInt(data.goals1),
          predicted_goals2: parseInt(data.goals2),
          // Estos campos se deben manejar con el user_id real del token en el backend
          user_id: "00000000-0000-0000-0000-000000000000", 
          group_id: "00000000-0000-0000-0000-000000000000"
        }));

      if (toSave.length === 0) {
        setMessage("No hay nuevos marcadores válidos para guardar.");
        setSaving(false);
        return;
      }

      await apiFetch("/predictions/bulk", {
        method: "POST",
        body: JSON.stringify(toSave),
      });
      setMessage("✅ ¡Marcadores guardados exitosamente!");
    } catch (err) {
      setMessage("❌ Error al guardar. Intenta de nuevo.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando partidos...</div>;

  return (
    <div className="min-h-screen bg-gray-100 pb-24">
      <header className="bg-green-700 text-white p-4 sticky top-0 z-10 shadow-md">
        <h1 className="text-xl font-bold text-center">Mis Pronósticos</h1>
      </header>

      <div className="max-w-md mx-auto p-4 space-y-4">
        {message && (
          <div className={`p-3 rounded-lg text-center text-sm font-bold shadow-sm ${message.includes("✅") ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
            {message}
          </div>
        )}

        {matches.map((match) => {
          const locked = isLocked(match.start_at);
          return (
            <div key={match.id} className={`bg-white rounded-xl shadow-sm p-4 border ${locked ? "opacity-75 border-gray-200" : "border-transparent"}`}>
              <div className="flex justify-between text-[10px] text-gray-500 mb-2 uppercase font-bold tracking-wider">
                <span>{match.phase === 'group' ? `Grupo ${match.group_name}` : match.phase}</span>
                <span>{new Date(match.start_at).toLocaleDateString()} - {new Date(match.start_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              </div>
              
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 text-right font-medium text-gray-800 truncate">{match.team1}</div>
                
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    disabled={locked}
                    className={`w-12 h-12 text-center text-xl font-bold border-2 rounded-lg outline-none transition-all ${locked ? "bg-gray-100 border-gray-200 text-gray-400" : "border-green-100 focus:border-green-500 text-green-700"}`}
                    value={predictions[match.id]?.goals1 || ""}
                    onChange={(e) => handleInputChange(match.id, 1, e.target.value)}
                  />
                  <span className="text-gray-300 font-bold">-</span>
                  <input
                    type="number"
                    disabled={locked}
                    className={`w-12 h-12 text-center text-xl font-bold border-2 rounded-lg outline-none transition-all ${locked ? "bg-gray-100 border-gray-200 text-gray-400" : "border-green-100 focus:border-green-500 text-green-700"}`}
                    value={predictions[match.id]?.goals2 || ""}
                    onChange={(e) => handleInputChange(match.id, 2, e.target.value)}
                  />
                </div>

                <div className="flex-1 text-left font-medium text-gray-800 truncate">{match.team2}</div>
              </div>
              
              {locked && (
                <div className="mt-2 text-center text-[10px] text-red-500 font-bold flex items-center justify-center gap-1">
                  <span className="text-xs">🔒</span> Partido bloqueado (Inicia pronto o ya finalizó)
                </div>
              )}
            </div>
          );
        })}
      </div>

      <footer className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t shadow-2xl flex justify-center max-w-md mx-auto">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full max-w-xs py-4 rounded-xl font-bold text-white shadow-lg transition-all transform active:scale-95 ${saving ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"}`}
        >
          {saving ? "Guardando..." : "Guardar todos mis cambios"}
        </button>
      </footer>
    </div>
  );
}
