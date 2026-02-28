const { Client } = require('pg');
const jwt = require('jsonwebtoken'); // Need to handle later if not installed

async function main() {
    const client = new Client({
        connectionString: 'postgresql://postgres:WGuhKWSeX9jQCRna@db.advgcyysxutgdvpjcphh.supabase.co:5432/postgres',
    });

    try {
        await client.connect();
        const res = await client.query("SELECT * FROM fsbb.users LIMIT 1");
        const user = res.rows[0];
        console.log("Found user:", user.email);

        // Generate token
        const secret = "fcb7eafe36047ec9cc9766d78c5b291db0812e8f5d865f948660e013cb2b66b3";
        // Fast API security.py: to_encode.update({"exp": expire})
        const token = require('crypto').createHmac('sha256', secret)
        // Wait, standard python jose uses base64url encoded JSON.
        // Let's just use Python for token generation since we can run python from Powershell if we use the right trick.
    } catch (err) {
        console.error(err);
    } finally {
        await client.end();
    }
}
main();
