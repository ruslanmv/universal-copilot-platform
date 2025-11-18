// Stub for tenant API calls
export async function listTenants() {
    return [
        { id: "tenant_a", name: "Example Tenant A", enabled_use_cases: ["support", "hr"], default_provider: "openai" }
    ];
}
export async function updateTenant(tenant: any) {
    console.log("Updating tenant", tenant);
    return tenant;
}
