import React, { useEffect, useState } from "react";
import { listTenants, updateTenant } from "../api/tenants";

interface Tenant {
  id: string;
  name: string;
  enabled_use_cases: string[];
  default_provider?: string;
}

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const data = await listTenants();
      setTenants(data);
      setLoading(false);
    })();
  }, []);

  const toggleUseCase = async (tenant: Tenant, useCase: string) => {
    const enabled = new Set(tenant.enabled_use_cases);
    if (enabled.has(useCase)) {
      enabled.delete(useCase);
    } else {
      enabled.add(useCase);
    }
    const updated = { ...tenant, enabled_use_cases: Array.from(enabled) };
    await updateTenant(updated);
    setTenants((prev) => prev.map((t) => (t.id === tenant.id ? updated : t)));
  };

  if (loading) return <p>Loading tenants…</p>;

  return (
    <section>
      <h2>Tenants</h2>
      <table>
        <thead>
          <tr>
            <th>Tenant</th>
            <th>Default Provider</th>
            <th>Enabled Use Cases</th>
          </tr>
        </thead>
        <tbody>
          {tenants.map((tenant) => (
            <tr key={tenant.id}>
              <td>{tenant.name}</td>
              <td>{tenant.default_provider ?? "inherit"}</td>
              <td>
                {["support", "hr", "legal"].map((uc) => (
                  <label key={uc} style={{ marginRight: 8 }}>
                    <input
                      type="checkbox"
                      checked={tenant.enabled_use_cases.includes(uc)}
                      onChange={() => toggleUseCase(tenant, uc)}
                    />
                    {uc}
                  </label>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
