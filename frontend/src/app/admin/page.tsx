"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Match {
  id: string;
  team1: string;
  team2: string;
  start_at: string;
  phase: string;
  is_finished: boolean;
  actual_goals1: number | null;
  actual_goals2: number | null;
}

export default function AdminPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [message, setMessage] = useState("");
  const [showAddMatch, setShowAddMatch] = useState(false);
  const [newMatch, setNewMatch] = useState({
    team1: "", team2: "", stadium: "", start_at: "", phase: "knockout"
  });
  const router = useRouter();

  useEffect(() => {
    const checkAdminAndFetch = async () => {
      try {
        const user = await apiFetch("/users/me");
        if (!user.is_superuser) {
          router.push("/groups");
          return;
        }
        setIsAdmin(true);
        const matchesData = await apiFetch("/matches");
        setMatches(matchesData.sort((a: Match, b: Match) => 
            new Date(b.start_at).getTime() - new Date(a.start_at).getTime()
        ));
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    checkAdminAndFetch();
  }, [router]);

  const handleUpdateResult = async (matchId: string, g1: number, g2: number) => {
    try {
      await apiFetch(`/admin/matches/${matchId}/results`, {
        method: "POST",
        body: JSON.stringify({ actual_goals1: g1, actual_goals2: g2, is_finished: true }),
      });
      setMessage("✅ Resultado actualizado y puntos calculados");
      // Refrescar lista
      const data = await apiFetch("/matches");
      setMatches(data.sort((a: Match, b: Match) => new Date(b.start_at).getTime() - new Date(a.start_at).getTime()));
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    }
  };

  const handleAddMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch("/admin/matches", {
        method: "POST",
        body: JSON.stringify(newMatch),
      });
      setShowAddMatch(false);
      setMessage("✅ Nuevo partido agregado al fixture");
      const data = await apiFetch("/matches");
      setMatches(data.sort((a: Match, b: Match) => new Date(b.start_at).getTime() - new Date(a.start_at).getTime()));
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    }
  };

  if (loading) return <div className="p-8 text-center font-bold">Verificando credenciales admin...</div>;
  if (!isAdmin) return null;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 max-w-2xl mx-auto pb-24">
      <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <div>
            <h1 className="text-2xl font-black text-red-500">Panel Admin</h1>
            <p className="text-xs text-gray-400 uppercase tracking-tighter">Gestión de Resultados</p>
        </div>
        <Link href="/groups" className="bg-gray-800 px-4 py-2 rounded-lg text-sm font-bold">Salir</Link>
      </header>

      {message && (
        <div className="mb-6 p-4 bg-gray-800 rounded-xl text-center font-bold border border-gray-700">
          {message}
        </div>
      )}

      <div className="mb-8">
        <button 
          onClick={() => setShowAddMatch(true)}
          className="w-full bg-blue-600 hover:bg-blue-700 py-4 rounded-2xl font-black transition shadow-lg shadow-blue-900/20"
        >
          + AGREGAR NUEVO PARTIDO
        </button>
      </div>

      <div className="space-y-4">
        <h2 className="text-sm font-bold text-gray-500 uppercase px-2">Partidos del Torneo</h2>
        {matches.map((m) => (
          <div key={m.id} className="bg-gray-800 p-5 rounded-2xl border border-gray-700 shadow-sm">
            <div className="flex justify-between text-[10px] text-gray-400 mb-3 uppercase font-bold tracking-widest">
              <span>{m.phase}</span>
              <span>{new Date(m.start_at).toLocaleString()}</span>
            </div>
            
            <div className="flex items-center justify-between gap-4 mb-4">
              <div className="flex-1 text-right font-bold truncate">{m.team1}</div>
              <div className="flex items-center gap-2">
                <input 
                    type="number" 
                    id={`g1-${m.id}`}
                    defaultValue={m.actual_goals1 ?? ""}
                    placeholder="?"
                    className="w-12 h-12 bg-gray-900 border border-gray-600 rounded-lg text-center text-xl font-black focus:border-red-500 outline-none"
                />
                <span className="text-gray-600">:</span>
                <input 
                    type="number" 
                    id={`g2-${m.id}`}
                    defaultValue={m.actual_goals2 ?? ""}
                    placeholder="?"
                    className="w-12 h-12 bg-gray-900 border border-gray-600 rounded-lg text-center text-xl font-black focus:border-red-500 outline-none"
                />
              </div>
              <div className="flex-1 text-left font-bold truncate">{m.team2}</div>
            </div>

            <button 
              onClick={() => {
                const g1 = (document.getElementById(`g1-${m.id}`) as HTMLInputElement).value;
                const g2 = (document.getElementById(`g2-${m.id}`) as HTMLInputElement).value;
                if (g1 !== "" && g2 !== "") handleUpdateResult(m.id, parseInt(g1), parseInt(g2));
              }}
              className={`w-full py-2 rounded-xl text-xs font-black tracking-widest transition ${m.is_finished ? "bg-gray-700 text-gray-400" : "bg-red-600 hover:bg-red-700 text-white"}`}
            >
              {m.is_finished ? "ACTUALIZAR RESULTADO" : "FINALIZAR PARTIDO"}
            </button>
          </div>
        ))}
      </div>

      {/* Modal Add Match */}
      {showAddMatch && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <form onSubmit={handleAddMatch} className="bg-gray-800 w-full max-w-sm rounded-3xl p-8 border border-gray-700 shadow-2xl">
            <h2 className="text-2xl font-black mb-6 text-blue-400">Nuevo Partido</h2>
            <div className="space-y-4">
                <input type="text" placeholder="Equipo Local" className="w-full bg-gray-900 p-3 rounded-xl border border-gray-600" required onChange={e => setNewMatch({...newMatch, team1: e.target.value})} />
                <input type="text" placeholder="Equipo Visitante" className="w-full bg-gray-900 p-3 rounded-xl border border-gray-600" required onChange={e => setNewMatch({...newMatch, team2: e.target.value})} />
                <input type="text" placeholder="Estadio" className="w-full bg-gray-900 p-3 rounded-xl border border-gray-600" onChange={e => setNewMatch({...newMatch, stadium: e.target.value})} />
                <input type="datetime-local" className="w-full bg-gray-900 p-3 rounded-xl border border-gray-600" required onChange={e => setNewMatch({...newMatch, start_at: e.target.value})} />
                <select className="w-full bg-gray-900 p-3 rounded-xl border border-gray-600" onChange={e => setNewMatch({...newMatch, phase: e.target.value})}>
                    <option value="group">Fase de Grupos</option>
                    <option value="knockout">Eliminatoria (KO)</option>
                </select>
            </div>
            <div className="flex gap-4 mt-8">
              <button type="button" onClick={() => setShowAddMatch(false)} className="flex-1 font-bold text-gray-400">CANCELAR</button>
              <button type="submit" className="flex-2 bg-blue-600 px-8 py-3 rounded-xl font-black">AGREGAR</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
