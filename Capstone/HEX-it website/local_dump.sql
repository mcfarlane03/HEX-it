--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Homebrew)
-- Dumped by pg_dump version 14.17 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Favourite; Type: TABLE; Schema: public; Owner: proj_user
--

CREATE TABLE public."Favourite" (
    id integer NOT NULL,
    user_id_fk integer NOT NULL,
    fav_user_id_fk integer NOT NULL
);


ALTER TABLE public."Favourite" OWNER TO proj_user;

--
-- Name: Favourite_id_seq; Type: SEQUENCE; Schema: public; Owner: proj_user
--

CREATE SEQUENCE public."Favourite_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Favourite_id_seq" OWNER TO proj_user;

--
-- Name: Favourite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: proj_user
--

ALTER SEQUENCE public."Favourite_id_seq" OWNED BY public."Favourite".id;


--
-- Name: Profile; Type: TABLE; Schema: public; Owner: proj_user
--

CREATE TABLE public."Profile" (
    id integer NOT NULL,
    user_id_fk integer NOT NULL,
    parish character varying(80),
    biography character varying(500),
    sex character varying(20),
    race character varying(20),
    birth_year integer,
    height double precision,
    fav_cuisine character varying(100),
    fav_colour character varying(50),
    fav_school_subject character varying(100),
    political boolean,
    religious boolean,
    family_oriented boolean,
    name character varying(255)
);


ALTER TABLE public."Profile" OWNER TO proj_user;

--
-- Name: Profile_id_seq; Type: SEQUENCE; Schema: public; Owner: proj_user
--

CREATE SEQUENCE public."Profile_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Profile_id_seq" OWNER TO proj_user;

--
-- Name: Profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: proj_user
--

ALTER SEQUENCE public."Profile_id_seq" OWNED BY public."Profile".id;


--
-- Name: Users; Type: TABLE; Schema: public; Owner: proj_user
--

CREATE TABLE public."Users" (
    id integer NOT NULL,
    username character varying(80),
    password character varying(255),
    name character varying(80),
    email character varying(128),
    photo character varying(255),
    date_joined timestamp without time zone
);


ALTER TABLE public."Users" OWNER TO proj_user;

--
-- Name: Users_id_seq; Type: SEQUENCE; Schema: public; Owner: proj_user
--

CREATE SEQUENCE public."Users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Users_id_seq" OWNER TO proj_user;

--
-- Name: Users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: proj_user
--

ALTER SEQUENCE public."Users_id_seq" OWNED BY public."Users".id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: proj_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO proj_user;

--
-- Name: Favourite id; Type: DEFAULT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Favourite" ALTER COLUMN id SET DEFAULT nextval('public."Favourite_id_seq"'::regclass);


--
-- Name: Profile id; Type: DEFAULT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Profile" ALTER COLUMN id SET DEFAULT nextval('public."Profile_id_seq"'::regclass);


--
-- Name: Users id; Type: DEFAULT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Users" ALTER COLUMN id SET DEFAULT nextval('public."Users_id_seq"'::regclass);


--
-- Data for Name: Favourite; Type: TABLE DATA; Schema: public; Owner: proj_user
--

COPY public."Favourite" (id, user_id_fk, fav_user_id_fk) FROM stdin;
2	5	1
3	7	1
7	1	9
8	1	7
14	5	8
15	1	5
21	5	7
22	5	9
\.


--
-- Data for Name: Profile; Type: TABLE DATA; Schema: public; Owner: proj_user
--

COPY public."Profile" (id, user_id_fk, parish, biography, sex, race, birth_year, height, fav_cuisine, fav_colour, fav_school_subject, political, religious, family_oriented, name) FROM stdin;
34	8	Parish1	Bio1	male	race1	1990	70	Cuisine1	Red	Math	t	f	t	Test Profile 1
35	9	Parish2	Bio2	female	race2	1992	65	Cuisine2	Blue	Science	f	t	f	Test Profile 2
39	7	St.James	Bio2	female	race2	1995	6	Cuisine2	Blue	Science	t	t	t	Cute Boy Paris Girl
40	7	St.James	Bio2	female	race2	1995	6	Cuisine2	Blue	Science	t	t	t	Cute Boy Paris Girl
44	5	Westmoreland	Student	female	African-American	2003	67	Cuisine2	blue	Science	t	f	f	Ner
45	5	Mand	Bio	female	African-American	2005	67	food	grenn	Science	t	f	f	D W
\.


--
-- Data for Name: Users; Type: TABLE DATA; Schema: public; Owner: proj_user
--

COPY public."Users" (id, username, password, name, email, photo, date_joined) FROM stdin;
1	nishlaw	pbkdf2:sha256:600000$aU8uYRAHBFbBTpxX$affb3667276894100f697213b50364c4a8bacd6ac042df95739fd79ebad59e01	Nishaun Lawrence	nishaun.lawrence@gmail.com	nishlaw_profile_photo.jpg	2025-05-01 13:11:55.447668
5	Nishaun	pbkdf2:sha256:600000$tDitKozOeCXDFZF7$e01fd185544e20fbfcf8e20c1c894313fe3080484dc5872d2bb5b4fc4a65446a	Mike James	john.doe@example.com	Nishaun_profile_photo.jpg	2025-05-01 14:05:45.118399
7	Paris	pbkdf2:sha256:600000$Ex5xLmxzQlEUfnfQ$8c326167578ba8435d77295ba616f728a43fffb7bf60fd92ebbf8d1b31cf74b4	Paris	john.doe@example.com	Paris_profile_photo.jpg	2025-05-02 12:03:55.668754
8	testuser1	pbkdf2:sha256:600000$i07UWOmBDX2S1AEN$272464dd1793e791e93023e59409032f74dd2d4a00045d90f8ce15d7a2a2f54b	Test User 1	test1@example.com	\N	2025-05-02 13:32:28.391833
9	testuser2	pbkdf2:sha256:600000$cWrWBJMW6ErBY3YW$6741b627e2c8ad32e25cace0d96b6476fae20a9c90d542bc5ee7378418b18ea1	Test User 2	test2@example.com	\N	2025-05-02 13:32:28.587193
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: proj_user
--

COPY public.alembic_version (version_num) FROM stdin;
c331a33fe448
\.


--
-- Name: Favourite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: proj_user
--

SELECT pg_catalog.setval('public."Favourite_id_seq"', 22, true);


--
-- Name: Profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: proj_user
--

SELECT pg_catalog.setval('public."Profile_id_seq"', 45, true);


--
-- Name: Users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: proj_user
--

SELECT pg_catalog.setval('public."Users_id_seq"', 9, true);


--
-- Name: Favourite Favourite_pkey; Type: CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Favourite"
    ADD CONSTRAINT "Favourite_pkey" PRIMARY KEY (id);


--
-- Name: Profile Profile_pkey; Type: CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Profile"
    ADD CONSTRAINT "Profile_pkey" PRIMARY KEY (id);


--
-- Name: Users Users_pkey; Type: CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY (id);


--
-- Name: Users Users_username_key; Type: CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_username_key" UNIQUE (username);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: Favourite Favourite_fav_user_id_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Favourite"
    ADD CONSTRAINT "Favourite_fav_user_id_fk_fkey" FOREIGN KEY (fav_user_id_fk) REFERENCES public."Users"(id);


--
-- Name: Favourite Favourite_user_id_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Favourite"
    ADD CONSTRAINT "Favourite_user_id_fk_fkey" FOREIGN KEY (user_id_fk) REFERENCES public."Users"(id);


--
-- Name: Profile Profile_user_id_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: proj_user
--

ALTER TABLE ONLY public."Profile"
    ADD CONSTRAINT "Profile_user_id_fk_fkey" FOREIGN KEY (user_id_fk) REFERENCES public."Users"(id);


--
-- PostgreSQL database dump complete
--

