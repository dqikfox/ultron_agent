Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-application-name, x-request-id, x-user-agent, x-forwarded-for',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, {
            status: 200,
            headers: corsHeaders
        });
    }
  
    try {
      // Get parameters from request body
      const requestBody = await req.json();
      const { email, password, role = 'authenticated' } = requestBody;
      
      if (!email || !password) {
        return new Response(JSON.stringify({
          error: { code: 'MISSING_PARAMS', message: 'Email and password are required' }
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 400,
        });
      }
  
      // Get environment variables
      const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
      const supabaseUrl = Deno.env.get('SUPABASE_URL');
      
      if (!serviceRoleKey || !supabaseUrl) {
        return new Response(JSON.stringify({
          error: { code: 'CONFIG_ERROR', message: 'Missing Supabase configuration' }
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500,
        });
      }
  
      // Generate user ID
      const userId = crypto.randomUUID();
      const now = new Date().toISOString();
      
      // Create user record (directly insert into auth.users table)
      const insertUserQuery = `
        INSERT INTO auth.users (
          id, email, encrypted_password, email_confirmed_at, 
          created_at, updated_at, role, aud, 
          confirmation_token, email_confirm_token_sent_at
        ) VALUES (
          $1, $2, crypt($3, gen_salt('bf')), $4,
          $5, $6, $7, 'authenticated',
          '', $8
        ) RETURNING id, email, created_at
      `;
      
      // Use fetch to call Supabase REST API
      const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${serviceRoleKey}`,
          'Content-Type': 'application/json',
          'apikey': serviceRoleKey,
        },
        body: JSON.stringify({
          query: insertUserQuery,
          params: [userId, email, password, now, now, now, role, now]
        })
      });
  
      if (!response.ok) {
        // If direct insert fails, try using Admin API to create user
        const adminResponse = await fetch(`${supabaseUrl}/auth/v1/admin/users`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'Content-Type': 'application/json',
            'apikey': serviceRoleKey,
          },
          body: JSON.stringify({
            email: email,
            password: password,
            email_confirm: true,
            user_metadata: { role: role }
          })
        });
  
        if (!adminResponse.ok) {
          const errorText = await adminResponse.text();
          return new Response(JSON.stringify({
            error: { 
              code: 'USER_CREATION_FAILED', 
              message: `Failed to create user: ${errorText}`,
              details: { status: adminResponse.status }
            }
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500,
          });
        }
  
        const userData = await adminResponse.json();
        return new Response(JSON.stringify({
          success: true,
          message: 'Admin user created successfully via Admin API',
          user: {
            id: userData.id,
            email: userData.email,
            created_at: userData.created_at,
            method: 'admin_api'
          }
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }
  
      const userData = await response.json();
      return new Response(JSON.stringify({
        success: true,
        message: 'Admin user created successfully via direct SQL',
        user: {
          id: userId,
          email: email,
          created_at: now,
          method: 'direct_sql'
        }
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
  
    } catch (error) {
      logger.error('Function error:', error);
      return new Response(JSON.stringify({
        error: { code: 'FUNCTION_ERROR', message: error.message }
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      });
    }
  });            
