"use client";

import { useEffect, useState, use } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

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

export default function GroupDashboard({ params }: { params: Promise<{ id: string }> }) {
  const { id: groupId } = use(params);
  const [matches, setMatches] = useState<Match[]>([]);
  const [predictions, setPredictions] = useState<PredictionState>({});
  const [groupName, setGroupName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Obtener info del grupo para el título
        const groups = await apiFetch("/groups");
        const currentGroup = groups.find((g: any) => g.id === groupId);
        if (currentGroup) setGroupName(currentGroup.name);

        const [matchesData, predsData] = await Promise.all([
          apiFetch("/matches"),
          apiFetch(`/groups/${groupId}/predictions/my`)
        ]);

        const sortedMatches = matchesData.sort((a: Match, b: Match) => 
          new Date(a.start_at).getTime() - new Date(b.start_at).getTime()
        );
        setMatches(sortedMatches);
        
        const initialPreds: PredictionState = {};
        sortedMatches.forEach((m: Match) => {
          initialPreds[m.id] = { goals1: "", goals2: "" };
        });

        predsData.forEach((p: any) => {
          if (initialPreds[p.match_id]) {
            initialPreds[p.match_id] = { 
              goals1: p.predicted_goals1.toString(), 
              goals2: p.predicted_goals2.toString() 
            };
          }
        });

        setPredictions(initialPreds);
      } catch (err) {
        console.error("Error fetching dashboard data", err);
        router.push("/groups");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [groupId, router]);

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
      const toSave = Object.entries(predictions)
        .filter(([matchId, data]) => {
          const match = matches.find(m => m.id === matchId);
          return data.goals1 !== "" && data.goals2 !== "" && match && !isLocked(match.start_at);
        })
        .map(([matchId, data]) => ({
          match_id: matchId,
          group_id: groupId,
          predicted_goals1: parseInt(data.goals1),
          predicted_goals2: parseInt(data.goals2),
        }));

      if (toSave.length === 0) {
        setMessage("No hay marcadores válidos para guardar.");
        setSaving(false);
        return;
      }

      await apiFetch("/predictions/bulk", {
        method: "POST",
        body: JSON.stringify(toSave),
      });
      setMessage("✅ ¡Marcadores guardados en este grupo!");
    } catch (err) {
      setMessage("❌ Error al guardar. Intenta de nuevo.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando polla...</div>;

  return (
    <div className="min-h-screen bg-gray-100 pb-24 font-sans">
      <header className="bg-green-700 text-white p-4 sticky top-0 z-10 shadow-md flex items-center justify-between">
        <Link href="/groups" className="text-white font-bold">← Grupos</Link>
        <div className="text-center flex-1">
            <h1 className="text-lg font-bold truncate">{groupName || "Mis Pronósticos"}</h1>
            <p className="text-[10px] uppercase tracking-widest opacity-80">Ingreso de Marcadores</p>
        </div>
        <div className="w-12"></div> {/* Spacer for alignment */}
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
            <div key={match.id} className={`bg-white rounded-2xl shadow-sm p-4 border ${locked ? "opacity-75 border-gray-200" : "border-transparent hover:border-green-200 transition-colors"}`}>
              <div className="flex justify-between text-[10px] text-gray-400 mb-3 uppercase font-bold tracking-wider">
                <span>{match.phase === 'group' ? `Grupo ${match.group_name}` : match.phase}</span>
                <span>{new Date(match.start_at).toLocaleDateString([], {day:'2-digit', month:'short'})} · {new Date(match.start_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              </div>
              
              <div className="flex items-center justify-between gap-2">
                <div className="flex-1 text-right font-bold text-gray-700 text-sm truncate">{match.team1}</div>
                
                <div className="flex items-center gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100">
                  <input
                    type="number"
                    disabled={locked}
                    className={`w-11 h-11 text-center text-xl font-black rounded-lg outline-none transition-all ${locked ? "bg-gray-100 text-gray-400" : "bg-white text-green-700 focus:ring-2 focus:ring-green-500 shadow-inner"}`}
                    value={predictions[match.id]?.goals1 || ""}
                    onChange={(e) => handleInputChange(match.id, 1, e.target.value)}
                  />
                  <span className="text-gray-300 font-bold">:</span>
                  <input
                    type="number"
                    disabled={locked}
                    className={`w-11 h-11 text-center text-xl font-black rounded-lg outline-none transition-all ${locked ? "bg-gray-100 text-gray-400" : "bg-white text-green-700 focus:ring-2 focus:ring-green-500 shadow-inner"}`}
                    value={predictions[match.id]?.goals2 || ""}
                    onChange={(e) => handleInputChange(match.id, 2, e.target.value)}
                  />
                </div>

                <div className="flex-1 text-left font-bold text-gray-700 text-sm truncate">{match.team2}</div>
              </div>
              
              {locked && (
                <div className="mt-2 text-center text-[9px] text-red-400 font-bold uppercase flex items-center justify-center gap-1">
                  🔒 Bloqueado
                </div>
              )}
            </div>
          );
        })}
      </div>

      <footer className="fixed bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-md border-t shadow-2xl flex justify-center z-20">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full max-w-md py-4 rounded-2xl font-black text-white shadow-xl transition-all transform active:scale-95 ${saving ? "bg-gray-400" : "bg-green-600 hover:bg-green-700 hover:shadow-green-200"}`}
        >
          {saving ? "GUARDANDO..." : "GUARDAR CAMBIOS"}
        </button>
      </footer>
    </div>
  );
}
