import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import TenantsPage from "./pages/TenantsPage";
import UseCasesPage from "./pages/UseCasesPage";
import ProvidersPage from "./pages/ProvidersPage";

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="logo">Universal Copilot Admin</h1>
        <nav>
          <NavLink to="/tenants">Tenants</NavLink>
          <NavLink to="/use-cases">Use Cases</NavLink>
          <NavLink to="/providers">Providers</NavLink>
        </nav>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/tenants" element={<TenantsPage />} />
          <Route path="/use-cases" element={<UseCasesPage />} />
          <Route path="/providers" element={<ProvidersPage />} />
          <Route path="*" element={<TenantsPage />} />
        </Routes>
      </main>
    </div>
  );
}
