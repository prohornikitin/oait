CREATE TABLE IF NOT EXISTS Publisher (
   id           SERIAL PRIMARY KEY,
   name         VARCHAR(255) NOT NULL,
   description  TEXT NOT NULL,
   bank_account CHAR(34) NOT NULL
);

CREATE TABLE IF NOT EXISTS "User" (
   id           SERIAL PRIMARY KEY,
   email        VARCHAR(255) NOT NULL,
   password     VARCHAR(255) NOT NULL,
   username     VARCHAR(255) NOT NULL,
   money        MONEY NOT NULL,
   publisher_id INT NULL REFERENCES Publisher(id)
);

CREATE TABLE IF NOT EXISTS Tag (
   id       SERIAL PRIMARY KEY,
   name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Product (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    description   TEXT NOT NULL,
    price         MONEY NOT NULL,
    reviews_count INT NOT NULL,
    rating_sum    INT NOT NULL,
    publisher_id  INT NOT NULL REFERENCES Publisher(id)
);

CREATE TABLE IF NOT EXISTS AssignedTag (
   tag_id      INT REFERENCES Tag(id) ON DELETE CASCADE,
   product_id  INT REFERENCES Product(id) ON DELETE CASCADE,
   PRIMARY KEY (tag_id, product_id)
);

CREATE TABLE IF NOT EXISTS Purchase (
   id         BIGSERIAL PRIMARY KEY,
   date       TIMESTAMP NOT NULL,
   buyer_id   INT NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
   product_id INT NOT NULL REFERENCES Product(id)
);

CREATE TABLE IF NOT EXISTS Gift (
   id           SERIAL PRIMARY KEY,
   title        VARCHAR(255) NOT NULL,
   message      TEXT NOT NULL,
   purchase_id  BIGINT NOT NULL REFERENCES Purchase(id),
   recipient_id INT NOT NULL REFERENCES "User"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Review (
   id         SERIAL PRIMARY KEY,
   rating     SMALLINT NOT NULL,
   text       TEXT NOT NULL,
   date       TIMESTAMP NOT NULL,
   writer_id  INT NOT NULL REFERENCES "User"(id),
   subject_id INT NOT NULL REFERENCES Product(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ProductDependency (
    primary_id   INT NOT NULL REFERENCES Product(id) ON DELETE CASCADE,
    dependant_id INT NOT NULL REFERENCES Product(id),
    PRIMARY KEY(primary_id, dependant_id)
);



CREATE OR REPLACE FUNCTION recalc_product_rating_stats_on_new_review()
 RETURNS TRIGGER AS $$
BEGIN
 UPDATE Product
   SET rating_sum = rating_sum + NEW.rating, reviews_count = reviews_count + 1
   WHERE NEW.subject_id = id;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER recalc_product_rating_stats_on_new_review
AFTER INSERT ON Review
FOR EACH ROW
EXECUTE PROCEDURE recalc_product_rating_stats_on_new_review();

CREATE OR REPLACE FUNCTION recalc_product_rating_stats_on_delete_review()
 RETURNS TRIGGER AS $$
BEGIN
 UPDATE Product
   SET rating_sum = rating_sum - OLD.rating, reviews_count = reviews_count - 1
   WHERE OLD.subject_id = id;
 RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER recalc_product_rating_stats_on_delete_review
AFTER DELETE ON Review
FOR EACH ROW
EXECUTE PROCEDURE recalc_product_rating_stats_on_delete_review();
