CREATE TABLE "bets"(
"id" INTEGER AUTO_INCREMENT PRIMARY KEY,
"discord_server_id" INTEGER,
"amount_a" INTEGER,
"amount_b" INTEGER,
"discord_user_id_a" INTEGER,
"discord_user_id_b" INTEGER,
"winner_discord_user_id" INT,
"status" TEXT
);

CREATE TABLE "users"(
"discord_user_id" INTEGER NOT NULL PRIMARY KEY,
"balance" INTEGER,
"wins" INTEGER,
"losses" INTEGER
);
