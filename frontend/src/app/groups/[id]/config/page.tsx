"use client";

import { useEffect, useState, use } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Config {
  pts_result_gr: number;
  pts_result_ko: number;
  pts_goals_gr: number;
  pts_goals_ko: number;
  pts_diff_gr: number;
  pts_diff_ko: number;
}

export default function GroupConfigPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await apiFetch(`/groups/${id}/config`);
        setConfig(data);
      } catch (err: any) {
        setMessage(`❌ ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchConfig();
  }, [id]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;
    setSaving(true);
    setMessage("");
    try {
      await apiFetch(`/groups/${id}/config`, {
        method: "PUT",
        body: JSON.stringify(config),
      });
      setMessage("✅ Reglas actualizadas correctamente");
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("¿Estás seguro de que quieres eliminar este grupo? Todos los pronósticos y configuraciones se perderán permanentemente.")) return;
    
    setSaving(true);
    try {
      await apiFetch(`/groups/${id}`, { method: "DELETE" });
      router.push("/groups");
    } catch (err: any) {
      setMessage(`❌ Error al eliminar: ${err.message}`);
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando reglas...</div>;
  if (!config) return <div className="p-8 text-center text-red-500 font-bold">{message || "No se pudo cargar la configuración"}</div>;

  const RuleInput = ({ label, field, phase }: { label: string, field: keyof Config, phase: string }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
      <div className="flex flex-col">
        <span className="text-sm font-bold text-gray-700">{label}</span>
        <span className="text-[10px] text-gray-400 uppercase tracking-wider">{phase}</span>
      </div>
      <input 
        type="number" 
        className="w-16 h-10 text-center font-bold text-green-700 border-2 border-green-100 rounded-lg outline-none focus:border-green-500 bg-white"
        value={config[field]}
        onChange={(e) => setConfig({ ...config, [field]: parseInt(e.target.value) || 0 })}
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6 max-w-xl mx-auto">
      <header className="flex items-center gap-4 mb-8">
        <Link href="/groups" className="text-green-700 font-bold">← Volver</Link>
        <h1 className="text-xl font-bold text-gray-800">Reglas de Puntuación</h1>
      </header>

      {message && (
        <div className={`p-4 mb-6 rounded-lg text-sm font-bold text-center shadow-sm ${message.includes("✅") ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleUpdate} className="space-y-8 pb-12">
        <section>
          <h2 className="text-xs font-bold text-gray-400 uppercase mb-4 tracking-widest px-1">Fase de Grupos</h2>
          <div className="space-y-3">
            <RuleInput label="Acertar Resultado" field="pts_result_gr" phase="Grupos" />
            <RuleInput label="Acertar Goles (x equipo)" field="pts_goals_gr" phase="Grupos" />
            <RuleInput label="Acertar Diferencia" field="pts_diff_gr" phase="Grupos" />
          </div>
        </section>

        <section>
          <h2 className="text-xs font-bold text-blue-400 uppercase mb-4 tracking-widest px-1">Fase Eliminatoria (KO)</h2>
          <div className="space-y-3">
            <RuleInput label="Acertar Resultado" field="pts_result_ko" phase="Eliminación" />
            <RuleInput label="Acertar Goles (x equipo)" field="pts_goals_ko" phase="Eliminación" />
            <RuleInput label="Acertar Diferencia" field="pts_diff_ko" phase="Eliminación" />
          </div>
        </section>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
          <p className="text-xs text-gray-500 italic">
            * Nota: Solo el creador del grupo puede guardar cambios o eliminar el grupo.
          </p>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-green-600 text-white font-bold py-4 rounded-2xl shadow-lg hover:bg-green-700 transition active:scale-95 disabled:bg-gray-400"
          >
            {saving ? "Guardando..." : "Guardar Configuración"}
          </button>
          
          <div className="pt-6 mt-6 border-t border-gray-100 text-center">
             <button
                type="button"
                onClick={handleDelete}
                disabled={saving}
                className="text-red-500 font-bold hover:underline text-sm"
              >
                Eliminar Grupo Definitivamente
             </button>
          </div>
        </div>
      </form>
    </div>
  );
}
