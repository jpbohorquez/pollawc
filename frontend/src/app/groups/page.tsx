"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Group {
  id: string;
  name: string;
  invite_code: string;
  creator_id: string;
}

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showJoin, setShowJoin] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  const fetchGroups = async () => {
    try {
      const data = await apiFetch("/groups");
      setGroups(data);
    } catch (err) {
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch("/groups", {
        method: "POST",
        body: JSON.stringify({ name: newGroupName }),
      });
      setNewGroupName("");
      setShowCreate(false);
      setMessage("✅ Grupo creado con éxito");
      fetchGroups();
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    }
  };

  const handleJoinGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch("/groups/join", {
        method: "POST",
        body: JSON.stringify({ invite_code: inviteCode }),
      });
      setInviteCode("");
      setShowJoin(false);
      setMessage("✅ Te has unido al grupo");
      fetchGroups();
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    }
  };

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando grupos...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 max-w-md mx-auto pb-24">
      <header className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Mis Grupos</h1>
        <Link href="/profile" className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-xl">👤</Link>
      </header>

      {message && (
        <div className={`p-4 mb-6 rounded-lg text-sm font-bold text-center shadow-sm ${message.includes("✅") ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {groups.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border-2 border-dashed border-gray-200">
            <p className="text-gray-400 mb-4">Aún no perteneces a ningún grupo</p>
          </div>
        ) : (
          groups.map((group) => (
            <div key={group.id} className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-gray-800 text-lg">{group.name}</h3>
                <p className="text-xs text-gray-500 font-mono mt-1">Código: <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-700 font-bold">{group.invite_code}</span></p>
              </div>
              <div className="flex gap-2">
                <Link 
                  href={`/groups/${group.id}/config`} 
                  className="p-2 bg-gray-50 rounded-lg text-gray-400 hover:text-green-600 transition"
                  title="Configuración"
                >
                  ⚙️
                </Link>
                <Link 
                  href="/dashboard" 
                  className="p-2 bg-green-600 rounded-lg text-white font-bold px-4"
                >
                  Jugar
                </Link>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="fixed bottom-6 left-6 right-6 flex gap-3 max-w-md mx-auto">
        <button 
          onClick={() => { setShowJoin(true); setShowCreate(false); }}
          className="flex-1 bg-blue-600 text-white font-bold py-4 rounded-2xl shadow-lg active:scale-95 transition"
        >
          Unirse a Grupo
        </button>
        <button 
          onClick={() => { setShowCreate(true); setShowJoin(false); }}
          className="flex-1 bg-green-600 text-white font-bold py-4 rounded-2xl shadow-lg active:scale-95 transition"
        >
          Crear Grupo
        </button>
      </div>

      {/* Modal Crear */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50">
          <div className="bg-white w-full max-w-xs rounded-2xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Nuevo Grupo</h2>
            <form onSubmit={handleCreateGroup}>
              <input 
                autoFocus
                type="text" 
                className="w-full p-3 border border-gray-200 rounded-lg mb-4 outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Nombre de la Polla"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                required
              />
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowCreate(false)} className="flex-1 py-3 text-gray-500 font-bold">Cancelar</button>
                <button type="submit" className="flex-1 bg-green-600 text-white font-bold rounded-lg">Crear</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Unirse */}
      {showJoin && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50">
          <div className="bg-white w-full max-w-xs rounded-2xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Unirse a Polla</h2>
            <form onSubmit={handleJoinGroup}>
              <input 
                autoFocus
                type="text" 
                className="w-full p-3 border border-gray-200 rounded-lg mb-4 outline-none focus:ring-2 focus:ring-blue-500 font-mono text-center uppercase tracking-widest"
                placeholder="CÓDIGO"
                maxLength={6}
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                required
              />
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowJoin(false)} className="flex-1 py-3 text-gray-500 font-bold">Cancelar</button>
                <button type="submit" className="flex-1 bg-blue-600 text-white font-bold rounded-lg">Unirse</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
