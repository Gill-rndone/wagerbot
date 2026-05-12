CREATE TABLE "wagers"(
"id" INTEGER UNIQUE NOT NULL PRIMARY KEY,
"discord_server_id" INTEGER,
"amount" INTEGER,
"discord_user_id_a" INTEGER,
"discord_user_id_b" INTEGER,
"winner_discord_user_id" INT,
"status" TEXT
);

CREATE TABLE "users"(
"discord_user_id" INTEGER NOT NULL PRIMARY KEY,
"discord_user_name" TEXT,
"balance" INTEGER,
"wins" INTEGER,
"losses" INTEGER
);
