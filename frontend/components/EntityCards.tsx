import React from "react";
import { Link, CreditCard, Phone, User, Fingerprint } from "lucide-react";

interface EntityCardsProps {
  entities: {
    upi_ids?: string[];
    urls?: string[];
    phones?: string[];
    names?: string[];
    bank_accounts?: string[];
  };
}

export function EntityCards({ entities }: EntityCardsProps) {
  const allEntities: { type: string; value: string; icon: React.ReactNode }[] = [];

  if (entities?.upi_ids) entities.upi_ids.forEach(e => allEntities.push({ type: "UPI ID", value: e, icon: <CreditCard size={16} /> }));
  if (entities?.urls) entities.urls.forEach(e => allEntities.push({ type: "URL", value: e, icon: <Link size={16} /> }));
  if (entities?.phones) entities.phones.forEach(e => allEntities.push({ type: "Phone", value: e, icon: <Phone size={16} /> }));
  if (entities?.names) entities.names.forEach(e => allEntities.push({ type: "Name", value: e, icon: <User size={16} /> }));
  if (entities?.bank_accounts) entities.bank_accounts.forEach(e => allEntities.push({ type: "Bank Account", value: e, icon: <Fingerprint size={16} /> }));

  if (allEntities.length === 0) {
    return <div className="text-gray-500 text-sm italic">No entities extracted yet.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {allEntities.map((ent, i) => (
        <div key={i} className="flex items-center gap-3 p-3 glass-panel rounded-lg border border-blue-500/20 hover:border-blue-500/50 transition-colors">
          <div className="p-2 bg-blue-500/10 rounded-md text-blue-400">
            {ent.icon}
          </div>
          <div className="flex flex-col truncate">
            <span className="text-xs text-gray-400 uppercase font-semibold tracking-wider">{ent.type}</span>
            <span className="text-sm text-gray-100 truncate font-mono">{ent.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
