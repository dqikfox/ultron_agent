SET session_replication_role = replica;

--
-- PostgreSQL database dump
--

-- \restrict YFa5224OsSJVS2v4zeEsAhN916Y1wa9z51kXRIJX0dJYt8j5UJgejKvhM33Wi9G

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: custom_oauth_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: oauth_clients; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: oauth_authorizations; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: oauth_client_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: oauth_consents; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: one_time_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: agent_memory; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."agent_memory" ("id", "key", "value", "memory_type", "created_at", "updated_at") VALUES
	('9f5ab874-02f1-4a9e-b18b-a6c82c378826', 'last_session_goal', '{"data": "Test Supabase integration"}', 'long_term', '2026-03-08 15:39:08.11687+00', '2026-03-08 15:39:08.115625+00'),
	('9964d695-e173-47e2-a37b-a2d380bc7b14', 'agent_version', '{"data": "3.0.4"}', 'long_term', '2026-03-08 15:39:08.120974+00', '2026-03-08 15:39:08.119977+00'),
	('301c317a-7699-4980-bbf1-7b2b3ea41b43', 'health_check_key', '{"status": "ok"}', 'long_term', '2026-03-08 16:28:33.000789+00', '2026-03-08 16:28:32.998931+00'),
	('8370b537-854e-4945-8379-5a10e2cdda67', 'health_check_key_v2', '{"status": "ok"}', 'long_term', '2026-03-08 16:29:33.040504+00', '2026-03-08 16:29:33.036789+00'),
	('22bc183f-6b76-44ea-8006-134dd8270bd8', 'test_key_integration', '{"data": "hello_world"}', 'long_term', '2026-03-08 16:11:16.435416+00', '2026-03-08 16:30:06.587862+00');


--
-- Data for Name: ai_providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."ai_providers" ("id", "provider_name", "base_url", "model_list", "is_active", "created_at") VALUES
	('00000000-0000-0000-0000-000000000101', 'ollama', 'http://localhost:11434', 'exaone-deep:7.8b,llama3.2:latest,qwen2.5:7b', true, NOW()),
	('00000000-0000-0000-0000-000000000102', 'openai', 'https://api.openai.com/v1', 'gpt-4o,gpt-4o-mini,gpt-3.5-turbo', false, NOW()),
	('00000000-0000-0000-0000-000000000103', 'nvidia', 'https://integrate.api.nvidia.com/v1', 'meta/llama-3.1-70b-instruct,nvidia/llama-3.1-nemotron-70b-instruct', false, NOW()),
	('00000000-0000-0000-0000-000000000104', 'bedrock', 'https://bedrock-runtime.us-east-1.amazonaws.com', 'anthropic.claude-3-5-sonnet-20241022-v2:0', false, NOW())
ON CONFLICT (id) DO NOTHING;



--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."conversations" ("id", "user_id", "title", "ai_provider", "model_name", "message_count", "created_at", "updated_at") VALUES
	('bee64b77-2583-44cd-903a-25c76426bcef', NULL, 'Test Session', 'ollama', 'exaone-deep:7.8b', 2, '2026-03-08 15:39:08.084618+00', '2026-03-08 15:39:08.106711+00'),
	('e50f0fc7-2531-475e-9451-26aa45b28cf5', NULL, 'Integration Test Session', 'ollama', 'local', 2, '2026-03-08 16:11:16.360932+00', '2026-03-08 16:11:16.397776+00'),
	('83415b95-b675-4a54-94bd-0ff623d56546', NULL, 'Tool Log Test', 'ollama', 'local', 0, '2026-03-08 16:11:16.496361+00', '2026-03-08 16:11:16.496361+00'),
	('590dc24d-9719-464c-bf22-41d49ff83491', NULL, 'Integration Test Session', 'ollama', 'local', 2, '2026-03-08 16:19:01.327007+00', '2026-03-08 16:19:01.348066+00'),
	('308daa76-681f-4437-9f77-c21a361101b5', NULL, 'Tool Log Test', 'ollama', 'local', 0, '2026-03-08 16:19:01.405921+00', '2026-03-08 16:19:01.405921+00'),
	('b6a81e76-e5c3-429a-9b51-fdc2504a89c1', NULL, 'health-check', 'ollama', 'local', 0, '2026-03-08 16:24:08.70186+00', '2026-03-08 16:24:08.70186+00'),
	('33bb9879-06f1-4f6d-a2d1-b1bfcc644fec', NULL, 'health-check-2026-03-08', 'ollama', 'local', 2, '2026-03-08 16:26:12.624881+00', '2026-03-08 16:26:12.650806+00'),
	('ab403d6a-7c68-4d04-b820-bb2c76908508', NULL, 'test-direct', 'ollama', 'local', 1, '2026-03-08 16:27:08.898124+00', '2026-03-08 16:27:08.906898+00'),
	('22aa1e04-290d-46f4-b533-d56542576006', NULL, 'health-check-final', 'ollama', 'local', 2, '2026-03-08 16:28:32.964662+00', '2026-03-08 16:28:32.985994+00'),
	('cc0faf99-132a-4262-aa7b-3f393d008cc5', NULL, 'health-check-final-v2', 'ollama', 'local', 2, '2026-03-08 16:29:32.977341+00', '2026-03-08 16:29:33.026346+00'),
	('f9477355-8dd4-4582-9cd8-56eab4c32ac0', NULL, 'Integration Test Session', 'ollama', 'local', 2, '2026-03-08 16:30:06.527973+00', '2026-03-08 16:30:06.553136+00'),
	('4fbdca5b-7615-4f49-bdfe-fb93247c3f05', NULL, 'Tool Log Test', 'ollama', 'local', 0, '2026-03-08 16:30:06.609887+00', '2026-03-08 16:30:06.609887+00');


--
-- Data for Name: file_uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."messages" ("id", "conversation_id", "user_id", "role", "content", "message_type", "file_url", "processing_time_ms", "tokens_used", "created_at") VALUES
	('3ab809aa-e2e4-4ef6-8763-442902fed406', 'bee64b77-2583-44cd-903a-25c76426bcef', NULL, 'user', 'Hello ULTRON, what can you do?', 'text', NULL, 0, 0, '2026-03-08 15:39:08.088508+00'),
	('243305f0-e91d-46f7-9c61-2ba737269d0d', 'bee64b77-2583-44cd-903a-25c76426bcef', NULL, 'assistant', 'I can help with many tasks!', 'text', NULL, 450, 20, '2026-03-08 15:39:08.099963+00'),
	('38b7d1b5-5ebe-4836-9023-8c329e7a5e8d', 'e50f0fc7-2531-475e-9451-26aa45b28cf5', NULL, 'user', 'Integration test message', 'text', NULL, 0, 0, '2026-03-08 16:11:16.377744+00'),
	('177cee0f-8f80-4c8f-85aa-b67e6914a3f3', 'e50f0fc7-2531-475e-9451-26aa45b28cf5', NULL, 'assistant', 'Integration test reply', 'text', NULL, 100, 0, '2026-03-08 16:11:16.392688+00'),
	('47fbcf87-ae78-42d6-925f-2b8d24798c5f', '590dc24d-9719-464c-bf22-41d49ff83491', NULL, 'user', 'Integration test message', 'text', NULL, 0, 0, '2026-03-08 16:19:01.333081+00'),
	('35eb8ec3-8e59-47bc-b32c-9d17857714e3', '590dc24d-9719-464c-bf22-41d49ff83491', NULL, 'assistant', 'Integration test reply', 'text', NULL, 100, 0, '2026-03-08 16:19:01.34315+00'),
	('83b22be2-c110-49cf-bc6c-957d1a87bd88', '00000000-0000-0000-0000-000000000001', NULL, 'user', 'hello test', 'text', NULL, NULL, NULL, '2026-03-08 16:26:34.669267+00'),
	('b5e1e20a-df44-460a-9907-67472056f0e7', NULL, NULL, 'user', 'aiohttp json= test', 'text', NULL, NULL, NULL, '2026-03-08 16:26:53.742929+00'),
	('884e2123-e7a3-4b0f-bf8b-c29d085af8d3', NULL, NULL, 'user', 'aiohttp json= test', 'text', NULL, NULL, NULL, '2026-03-08 16:26:53.748719+00'),
	('3e530cbc-97b2-457f-993b-8a22f431ae23', 'ab403d6a-7c68-4d04-b820-bb2c76908508', NULL, 'user', 'hello direct test', 'text', NULL, NULL, NULL, '2026-03-08 16:27:26.086774+00'),
	('d32cf781-16df-4d15-ac9b-95a0225ead54', '22aa1e04-290d-46f4-b533-d56542576006', NULL, 'user', 'hello from health check', 'text', NULL, 0, 0, '2026-03-08 16:28:32.96994+00'),
	('a9789f4f-6c2a-4566-a83d-9fcd57230507', '22aa1e04-290d-46f4-b533-d56542576006', NULL, 'assistant', 'all systems nominal', 'text', NULL, 0, 0, '2026-03-08 16:28:32.980402+00'),
	('07609e29-c6b3-4645-b308-e8872ca593ca', 'cc0faf99-132a-4262-aa7b-3f393d008cc5', NULL, 'user', 'hello from health check', 'text', NULL, 0, 0, '2026-03-08 16:29:32.988964+00'),
	('32da1e3a-89fc-4315-ac15-47c90792f8b9', 'cc0faf99-132a-4262-aa7b-3f393d008cc5', NULL, 'assistant', 'all systems nominal', 'text', NULL, 0, 0, '2026-03-08 16:29:33.020093+00'),
	('92882641-e154-4ddb-947c-83f2d2a905e1', 'f9477355-8dd4-4582-9cd8-56eab4c32ac0', NULL, 'user', 'Integration test message', 'text', NULL, 0, 0, '2026-03-08 16:30:06.536453+00'),
	('912802ba-6374-4e91-a85d-c78ff80c2c09', 'f9477355-8dd4-4582-9cd8-56eab4c32ac0', NULL, 'assistant', 'Integration test reply', 'text', NULL, 100, 0, '2026-03-08 16:30:06.547991+00');


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: tool_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."tool_executions" ("id", "tool_name", "input", "output", "status", "duration_ms", "session_id", "created_at") VALUES
	('750f70fd-f1c6-4dc2-8c42-47eaebcecedd', 'web_search', 'latest AI news', 'Found 5 articles', 'success', 320, 'bee64b77-2583-44cd-903a-25c76426bcef', '2026-03-08 15:39:08.112456+00'),
	('d20d777e-83f3-402d-86be-08ebe781a7fc', 'test_tool', 'test input', 'test output', 'success', 42, '83415b95-b675-4a54-94bd-0ff623d56546', '2026-03-08 16:11:16.505785+00'),
	('7c790efa-f550-46d6-83e2-d9088bad6734', 'test_tool', 'test input', 'test output', 'success', 42, '308daa76-681f-4437-9f77-c21a361101b5', '2026-03-08 16:19:01.413301+00'),
	('d0f585f6-6daa-4bf7-a293-1d33192e0d64', 'health_check_tool', 'ping', '{"ok": true}', 'success', 0, '22aa1e04-290d-46f4-b533-d56542576006', '2026-03-08 16:28:32.993298+00'),
	('a7ae672a-426e-4815-b6c9-bb2fdc34276c', 'health_check_tool', 'ping', '{"ok": true}', 'success', 0, 'cc0faf99-132a-4262-aa7b-3f393d008cc5', '2026-03-08 16:29:33.030836+00'),
	('1c4ad8e9-1666-4d21-a10a-bd4b29109532', 'test_tool', 'test input', 'test output', 'success', 42, '4fbdca5b-7615-4f49-bdfe-fb93247c3f05', '2026-03-08 16:30:06.613411+00');


--
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: buckets_analytics; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: buckets_vectors; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: iceberg_namespaces; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: iceberg_tables; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: s3_multipart_uploads; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: s3_multipart_uploads_parts; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: vector_indexes; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: hooks; Type: TABLE DATA; Schema: supabase_functions; Owner: supabase_functions_admin
--



--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: supabase_auth_admin
--

SELECT pg_catalog.setval('"auth"."refresh_tokens_id_seq"', 1, false);


--
-- Name: hooks_id_seq; Type: SEQUENCE SET; Schema: supabase_functions; Owner: supabase_functions_admin
--

SELECT pg_catalog.setval('"supabase_functions"."hooks_id_seq"', 1, false);


--
-- PostgreSQL database dump complete
--

-- \unrestrict YFa5224OsSJVS2v4zeEsAhN916Y1wa9z51kXRIJX0dJYt8j5UJgejKvhM33Wi9G

RESET ALL;
