-- 1. Вывести всю библиотеку игр (Product) пользователя c User.id = 1
WITH library_purchases AS (
	SELECT g.purchase_id
		FROM Gift AS g
		WHERE recipient_id = 1
	UNION ALL
	SELECT pur.id AS purchase_id
		FROM (SELECT * FROM Purchase AS pur WHERE pur.buyer_id = 1) AS pur
		LEFT JOIN Gift AS g
		ON pur.id = g.purchase_id
		WHERE g.purchase_id IS NULL
)
SELECT DISTINCT ON (prod.id) prod.*, pur.date
	FROM library_purchases AS lib_pur
	INNER JOIN Purchase AS pur
	ON lib_pur.purchase_id = pur.id
	INNER JOIN Product AS prod
	ON pur.product_id = prod.id;


-- 2. Получение средней оценки товара по отзывам (c ID = 12)
SELECT 
	CASE reviews_count 
		WHEN 0 THEN 0
		ELSE DIV(rating_sum, reviews_count)
	END AS avg_rating
	FROM Product
	WHERE id = 12;

-- 3. Получить 10 самых популярных продуктов (по продажам)
SELECT COUNT(1) as sales, product_id FROM Purchase
	GROUP BY product_id
	ORDER BY sales DESC
	LIMIT 10;


-- 4. Вывести весь не купленный пользователем дополнительный контент для некоторой игры (Product, ProductDependency) (1)
WITH RECURSIVE all_deps AS (
    SELECT DISTINCT
        Game.id,
        1 AS parent,
        0 AS level
    FROM Product Game
        WHERE Game.id = 3
    UNION ALL
    SELECT
        Dep.id,
        prev.id,
        level + 1
    FROM all_deps AS prev
    INNER JOIN ProductDependency AS DepLink
        ON prev.id = DepLink.primary_id
    INNER JOIN Product AS Dep
        ON Dep.id = DepLink.dependant_id
),
library_purchases AS (
	SELECT g.purchase_id
		FROM Gift AS g
		WHERE recipient_id = 1
	UNION ALL
	SELECT pur.id AS purchase_id
		FROM (SELECT * FROM Purchase AS pur WHERE pur.buyer_id = 1) AS pur
		LEFT JOIN Gift AS g
		ON pur.id = g.purchase_id
		WHERE g.purchase_id IS NULL
),
lib AS (
    SELECT DISTINCT ON (prod.id) prod.*, pur.date
    FROM library_purchases AS lib_pur
    INNER JOIN Purchase AS pur
        ON lib_pur.purchase_id = pur.id
    INNER JOIN Product AS prod
        ON pur.product_id = prod.id
)
SELECT id FROM all_deps
    WHERE level != 0 AND id NOT IN (SELECT id FROM lib);


-- 5. Вывести все игры с набором тегов (Tag), аналогичным набору тегов игры с Product.id = 1

WITH product_tags AS (
	SELECT at.tag_id 
	FROM AssignedTag AS at 
	WHERE at.product_id = 1
), products_with_tags_count AS (
	SELECT product_id, COUNT(*) AS all_tags, COUNT(product_tags.tag_id) AS coincided_tags
		FROM AssignedTag AS at
		LEFT JOIN product_tags
		USING (tag_id)
		GROUP BY at.product_id
)
SELECT prod.*
	FROM (SELECT * FROM products_with_tags_count WHERE products_with_tags_count.all_tags = products_with_tags_count.coincided_tags) AS products_with_no_other_tags
	INNER JOIN (SELECT COUNT(*) AS needed_tags FROM product_tags) AS needed_tags_count
	ON needed_tags_count.needed_tags = products_with_no_other_tags.all_tags
	INNER JOIN Product AS prod
	ON prod.id = products_with_no_other_tags.product_id;




-- 6. Вывести все подарки (Gift), сделанные пользователю c User.id = 280, по убыванию даты

SELECT g.id AS gift_id, g.title, g.message, p.product_id, p.date
	FROM Gift AS g
	INNER JOIN Purchase AS p
	ON g.recipient_id = 280 AND g.purchase_id = p.id
	ORDER BY date DESC;







-- 2. Вывести 10 издателей (Publisher), лидирующих по объему продаж их игр

WITH publisher_sales AS (
	SELECT publisher_id, SUM(purchasers_count) AS sales
	FROM Product AS prod
	GROUP BY publisher_id
)
SELECT pub.id AS pub_id, pub.name, pub.description, s.sales
	FROM publisher_sales AS s
	INNER JOIN Publisher AS pub
	ON s.publisher_id = pub.id
	ORDER BY sales DESC
	LIMIT 10;


-- 3. Сгруппировать игры издателя с Publisher.id = 1 по тегам и вывести эти теги в порядке убывания частоты их появления

WITH publisher_tags AS (
	SELECT prod.publisher_id, at.tag_id, COUNT(*) AS tag_count
	FROM Product AS prod
	INNER JOIN AssignedTag AS at
		ON prod.id = at.product_id
	WHERE prod.publisher_id = 1
	GROUP BY prod.publisher_id, at.tag_id
	ORDER BY tag_count DESC
)
SELECT pt.publisher_id, pub.name AS publisher_name, pt.tag_id, t.name AS tag_name, pt.tag_count
	FROM publisher_tags AS pt
	INNER JOIN Publisher AS pub
	ON pub.id = pt.publisher_id
	INNER JOIN Tag AS t
	ON pt.tag_id = t.id;
	



-- 5. Вывести последний положительный (Review.rating > 3.0) и последний отрицательный (Review.rating <= 3.0) обзоры (Review) 
-- на игру с Product.id = 1, авторами которых являются пользователи, написавшие не менее 2-х обзоров РАНЕЕ

WITH reliable_reviews AS (
	SELECT rev.*, row_number() OVER (PARTITION BY rev.writer_id ORDER BY rev.date ASC) AS ordinal
	FROM Review AS rev
)
SELECT * FROM
(
	SELECT 
		rel_rev.id,
		rel_rev.rating,
		rel_rev.text,
		rel_rev.date,
		rel_rev.writer_id,
		rel_rev.subject_id
	FROM reliable_reviews AS rel_rev
	WHERE rel_rev.subject_id = 1 AND rel_rev.ordinal >= 2 AND rel_rev.rating > 3
	ORDER BY date DESC
	LIMIT 1
)
UNION ALL
SELECT * FROM (
	SELECT
		rel_rev.id,
		rel_rev.rating,
		rel_rev.text,
		rel_rev.date,
		rel_rev.writer_id,
		rel_rev.subject_id
	FROM reliable_reviews AS rel_rev
	WHERE rel_rev.subject_id = 1 AND rel_rev.ordinal>=2 AND rel_rev.rating<=3
	ORDER BY date DESC
	LIMIT 1
);





-- 7. Вывести 10 самых продаваемых игр за последние 30 дней [или за текущий месяц? или за год? или как лучше то?]

WITH product_sales AS (
	SELECT pur.product_id, COUNT(*) AS last_30_days_sales
	FROM Purchase AS pur
	WHERE pur.date > CURRENT_TIMESTAMP - INTERVAL '30 days'
	GROUP BY pur.product_id
	ORDER BY last_30_days_sales DESC
	LIMIT 10
)
SELECT prod.*, sales.last_30_days_sales
	FROM product_sales as sales
	INNER JOIN Product as prod
	ON sales.product_id = prod.id
	ORDER BY last_30_days_sales DESC;


-




-- найти суммарную стоимость продууктов предыдущего запроса (2)
WITH RECURSIVE all_deps AS (
    SELECT DISTINCT
        Game.id,
        -1 AS parent,
        0 AS level
    FROM Product Game
    WHERE Game.id = 1
    UNION ALL
    SELECT
        Dep.id,
        prev.id,
        level + 1
    FROM all_deps AS prev
    INNER JOIN ProductDependency AS DepLink
        ON prev.id = DepLink.primary_id
    INNER JOIN Product AS Dep
        ON Dep.id = DepLink.dependant_id
),
library_purchases AS (
	SELECT g.purchase_id
		FROM Gift AS g
		WHERE recipient_id = 1
	UNION ALL
	SELECT pur.id AS purchase_id
		FROM (SELECT * FROM Purchase AS pur WHERE pur.buyer_id = 1) AS pur
		LEFT JOIN Gift AS g
		ON pur.id = g.purchase_id
		WHERE g.purchase_id IS NULL
),
lib AS (
    SELECT DISTINCT ON (prod.id) prod.*, pur.date
    FROM library_purchases AS lib_pur
    INNER JOIN Purchase AS pur
        ON lib_pur.purchase_id = pur.id
    INNER JOIN Product AS prod
        ON pur.product_id = prod.id
)
SELECT SUM(Product.price) FROM all_deps
	INNER JOIN Product 
		ON Product.id = all_deps.id;
	WHERE (level != 0 AND id NOT IN (SELECT id FROM lib))
