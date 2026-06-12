"use client";

import { useEffect, useState, use } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface LeaderboardEntry {
  user_id: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  total_points: number;
  predictions_count: number;
}

interface LeaderboardData {
  group_id: string;
  entries: LeaderboardEntry[];
}

export default function GroupRankingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const result = await apiFetch(`/groups/${id}/leaderboard`);
        setData(result);
      } catch (err: any) {
        setMessage(`❌ ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchRanking();
  }, [id]);

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando posiciones...</div>;
  if (!data) return <div className="p-8 text-center text-red-500 font-bold">{message || "No se pudo cargar el ranking"}</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 max-w-xl mx-auto">
      <header className="flex items-center gap-4 mb-8">
        <Link href="/groups" className="text-green-700 font-bold">← Volver</Link>
        <h1 className="text-2xl font-bold text-gray-800">Ranking del Grupo</h1>
      </header>

      {message && (
        <div className="p-4 mb-6 bg-red-100 text-red-800 rounded-lg text-sm font-bold text-center">
          {message}
        </div>
      )}

      <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
        <div className="bg-green-700 p-6 text-white text-center">
          <p className="text-xs uppercase tracking-widest opacity-80 mb-1">Puntero Actual</p>
          {data.entries.length > 0 ? (
            <div>
                <h2 className="text-3xl font-black">{data.entries[0].username}</h2>
                <p className="text-lg font-bold mt-1">{data.entries[0].total_points} Puntos</p>
            </div>
          ) : (
            <p className="font-bold italic opacity-60">Aún no hay participantes</p>
          )}
        </div>

        <div className="p-2">
          <table className="w-full">
            <thead>
              <tr className="text-[10px] text-gray-400 uppercase tracking-widest border-b border-gray-50">
                <th className="py-4 px-2 text-center w-12">Pos</th>
                <th className="py-4 px-2 text-left">Participante</th>
                <th className="py-4 px-2 text-right">Pts</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {data.entries.map((entry, index) => (
                <tr key={entry.user_id} className={`hover:bg-gray-50 transition ${index === 0 ? "bg-yellow-50/50" : ""}`}>
                  <td className="py-4 px-2 text-center">
                    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full font-black text-xs ${
                        index === 0 ? "bg-yellow-400 text-yellow-900" : 
                        index === 1 ? "bg-gray-300 text-gray-700" : 
                        index === 2 ? "bg-orange-300 text-orange-900" : 
                        "text-gray-400"
                    }`}>
                        {index + 1}
                    </span>
                  </td>
                  <td className="py-4 px-2">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
                            {entry.avatar_url ? (
                                <img src={entry.avatar_url} alt="Av" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-sm">👤</div>
                            )}
                        </div>
                        <div className="flex flex-col min-w-0">
                            <span className="font-bold text-gray-800 text-sm truncate">{entry.full_name || entry.username}</span>
                            <span className="text-[10px] text-gray-400 truncate">@{entry.username} · {entry.predictions_count} pronósticos</span>
                        </div>
                    </div>
                  </td>
                  <td className="py-4 px-2 text-right">
                    <span className="font-black text-green-700">{entry.total_points}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-8 text-center text-xs text-gray-400 italic">
        * El ranking se actualiza automáticamente cuando el administrador carga los resultados reales.
      </div>
    </div>
  );
}
