import sqlite3
import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    # ======================================================================================================================
    # ===== ТАБЛИЦА: users =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_users_user(self, user_id, user_link, user_reg_time, user_name=None, user_first_name=None,
                       user_last_name=None, coin_count=0):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO users (user_id, user_link, user_name, user_first_name, user_last_name, user_reg_time, foodToMoodCoin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_link, user_name, user_first_name, user_last_name, user_reg_time, coin_count))

    def del_users_user(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM users WHERE user_id = ?",
                (user_id,))

    def check_users_user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchall()
            return bool(len(result))

    # --- Ban ---

    def set_users_ban(self, user_id: int, ban: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET ban = ? WHERE user_id = ?", (ban, user_id))

    def get_users_ban(self, user_id) -> dict:
        with self.connection:
            result = self.connection.execute("SELECT ban FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            return bool(int(result[0][0]))

    # --- Mode ---

    def set_users_mode(self, user_id: int, mode_id: int, mode_key: str):
        with self.connection:
            self.cursor.execute("UPDATE users SET mode_id = ?, mode_key = ? WHERE user_id = ?",
                                (mode_id, mode_key, user_id))

    def get_users_mode(self, user_id) -> dict:
        with self.connection:
            result = self.connection.execute("SELECT mode_id, mode_key FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            return {'id': int(result[0][0]), 'key': str(result[0][1])}

    # --- Message ---

    def set_users_first_message(self, user_id, id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET first_message = ? WHERE user_id = ?", (id, user_id))

    def get_users_first_message(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT first_message FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            for row in result:
                id = str(row[0])
                return id
            return 0

    def set_users_last_message(self, user_id, id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET last_message = ? WHERE user_id = ?", (id, user_id))

    def get_users_last_message(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT last_message FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            for row in result:
                id = str(row[0])
                return id
            return 0

    # --- User link ---

    def get_users_user_link(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_link FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_link = str(row[0])
            return user_link

    # --- User name ---

    def get_users_user_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_name = str(row[0])
            return user_name

    # --- User first name ---

    def get_users_user_first_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_first_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_first_name = str(row[0])
            return user_first_name

    # --- User last name ---

    def get_users_user_last_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_last_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_last_name = str(row[0])
            return user_last_name

    # --- User reg time ---

    def get_users_user_reg_time(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_reg_time FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_reg_time = str(row[0])
            return user_reg_time

            # --- User last recommendation time ---

    # def set_users_last_recomendation_time(self, user_id, current_time):
    #             with self.connection:
    #                 return self.cursor.execute(
    #                     "UPDATE users SET last_recomendation_time = ? FROM users WHERE user_id = ?",
    #                     (user_id, current_time))

    def get_users_last_recomendation_time(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT last_recomendation_time FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

        for row in result:
            last_recomendation_time = str(row[0])
            return last_recomendation_time

    # --- Food2Mood Coin
    def add_food_to_mood_coin(self, user_id: int, coin_count: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET foodToMoodCoin = foodToMoodCoin + ? WHERE user_id = ?",
                                (coin_count, user_id))

    def clear_food_to_mood_coin(self, user_id: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET foodToMoodCoin = foodToMoodCoin + ? WHERE user_id = ?", (user_id,))

    def get_users_food_to_mood_coin(self, user_id: int):
        with self.connection:
            result = self.connection.execute("SELECT foodToMoodCoin FROM users WHERE user_id = ?", (user_id,))
            for row in result:
                foodToMoodCoin = str(row[0])
            return foodToMoodCoin

    # --- All users ---

    def get_users_users(self):
        with self.connection:
            result = self.connection.execute("SELECT user_id FROM users").fetchall()
            users_id = []
            for row in result:
                users_id.append(int(row[0]))
            return users_id

    # ======================================================================================================================
    # ===== ТАБЛИЦА: clients =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_client(self, user_id, username=None):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO clients (id, username) VALUES (?, ?)",
                (user_id, username))

    def del_client(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM clients WHERE id = ?",
                (user_id,))

    def check_client(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM clients WHERE id=?",
                (user_id,)).fetchall()
            if not bool(len(result)):
                return False
            elif result[0][4] == 'None' or result[0][4] is None:
                return False
            else:
                return True

    def all_client(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM clients").fetchall()
            return result

    # --- Username ---

    def set_client_username(self, user_id: int, username: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET username = ? WHERE id = ?",
                (username, user_id))

    def get_client_username(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT username FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- Sex ---

    def set_client_sex(self, user_id: int, sex: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET sex = ? WHERE id = ?",
                (sex, user_id))

    def get_client_sex(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT sex FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- Age ---

    def set_client_age(self, user_id: int, age: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET age = ? WHERE id = ?",
                (age, user_id))

    def get_client_age(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT age FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- Style ---

    def set_client_style(self, user_id: int, style: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET style = ? WHERE id = ?",
                (style, user_id))

    def get_client_style(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT style FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- Ccal ---
    def set_client_ccal(self, user_id: int, ccal: int):
        with self.connection:
            self.cursor.execute('UPDATE clients SET ccal=? WHERE id=?', (ccal, user_id))
    def get_client_ccal(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT ccal FROM clients WHERE id = ?", (user_id,)).fetchall()
            return str(result[0][0])
    # --- Blacklist ---

    def set_client_blacklist(self, user_id: int, blacklist: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET blacklist = ? WHERE id = ?",
                (blacklist, user_id))

    def get_client_blacklist(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT blacklist FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            for row in result:
                blacklist = str(row[0])
            return blacklist

    # --- Whitelist ---

    def set_client_whitelist(self, user_id: int, whitelist: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET whitelist = ? WHERE id = ?",
                (whitelist, user_id))

    def get_client_whitelist(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT whitelist FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            for row in result:
                whitelist = str(row[0])
            return whitelist

    # --- temp_rest ---
    def set_new_review(self, date, user_name, rating, review, dish_name, restaurant_name):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO reviews(date, user_name, rating, review, dish_name, restaurant_name) VALUES (?, ?, ?, ?, ?, ?)",
                (date, user_name, rating, review, dish_name, restaurant_name))

    def get_reviews(self, rest_name):
        with self.connection:
            result = self.connection.execute("SELECT date, dish_name, rating, review FROM reviews WHERE restaurant_name = ?",
                                             (rest_name,)).fetchall()
            # Использование множества для удаления дубликатов и преобразование его обратно в список
            return result

    def set_client_temp_rest(self, user_id: int, temp_rest: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_rest = ? WHERE id = ?",
                (temp_rest, user_id))

    def get_client_temp_rest(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_rest FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    def get_img_dish(self, dish_id: int):
        result = self.connection.execute(
            "SELECT images FROM restaurants WHERE id = ?",
            (dish_id,)
        ).fetchone()

        if result:
            # Assuming the images column contains the image URL
            image_url = result['images']
            return image_url
        else:
            return None

    # --- temp_state ---

    def set_client_temp_mood(self, user_id: int, temp_state: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_state = ? WHERE id = ?",
                (temp_state, user_id))

    def get_client_temp_mood(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_state FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- temp_recommendation ---

    def set_client_temp_recommendation(self, user_id: int, temp_recommendation: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_recommendation = ? WHERE id = ?",
                (temp_recommendation, user_id))

    def get_client_temp_recommendation(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_recommendation FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- temp_category ---

    def set_client_temp_category(self, user_id: int, temp_category: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_category = ? WHERE id = ?",
                (temp_category, user_id))

    def get_client_temp_category(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_category FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # --- temp_dish ---

    def set_client_temp_dish(self, user_id: int, temp_dish: int):
        temp_dish = max(temp_dish, 0)
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_dish = ? WHERE id = ?",
                (temp_dish, user_id))

    def get_client_temp_dish(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_dish FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    # --- temp_dish_id ---

    def set_client_temp_dish_id(self, user_id: int, temp_dish_id: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET temp_dish_id = ? WHERE id = ?",
                (temp_dish_id, user_id))

    def get_client_temp_dish_id(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_dish_id FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    # --- can_alert ---

    def set_client_can_alert(self, user_id: int, can_alert: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET can_alert = ? WHERE id = ?",
                (can_alert, user_id))

    def get_client_can_alert(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT can_alert FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    def set_client_last_qr_time(self, user_id: int, last_qr_time: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET last_qr_time = ? WHERE id = ?",
                (last_qr_time, user_id))

    def get_client_last_qr_time(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT last_qr_time FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    def set_client_rec_message_id(self, user_id: int, rec_message_id: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET rec_message_id = ? WHERE id = ?",
                (rec_message_id, user_id))

    def get_client_rec_message_id(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT rec_message_id FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    def get_dish_price(self, id) -> str:
        with self.connection:
            result = self.cursor.execute(
                "SELECT dish_price FROM restaurants WHERE id = ?",
                (id,)).fetchall()
            return result

    def get_g(self, id) -> str:
        with self.connection:
            result = self.cursor.execute(
                "SELECT dish_g FROM restaurants WHERE id = ?",
                (id,)).fetchall()
            return result

    def set_client_recommendation(self, user_id: int, recommendation: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET recommendation = ? WHERE id = ?",
                (recommendation, user_id))

    def get_client_recommendation(self, user_id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT recommendation FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    def set_client_filter(self, user_id: int, filter: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE clients SET filter = ? WHERE id = ?",
                (filter, user_id))

    def get_client_filter(self, user_id: int) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT filter FROM clients WHERE id = ?",
                (user_id,)).fetchall()
            return str(result[0][0])

    # ======================================================================================================================
    # ===== ТАБЛИЦА: restaurants =================================================================================================
    # ======================================================================================================================
    # --- all categories ---
    # --- all categories ---
    def restaurants_get_all_categories(self, rest_name):
        with self.connection:
            result = self.connection.execute("SELECT dish_category FROM restaurants WHERE rest_name = ?",
                                             (rest_name,)).fetchall()
            # Использование множества для удаления дубликатов и преобразование его обратно в список
            unique_categories = list(set(category[0] for category in result))
            return unique_categories

    def restaurants_find_all(self, keyword):
        with self.connection:
            self.connection.execute("DROP TABLE IF EXISTS rest_fts")
            self.connection.execute("CREATE VIRTUAL TABLE rest_fts USING fts4(id, rest_name, rest_address)")
            self.connection.execute("INSERT INTO rest_fts(id, rest_name, rest_address) "
                                    "SELECT id, rest_name, rest_address "
                                    "FROM restaurants")
            result = self.connection.execute(
                f"SELECT id, rest_name, rest_address FROM rest_fts WHERE rest_name LIKE '%{keyword}%' OR rest_address LIKE '%{keyword}%'").fetchall()
            all_posts = []
            rest = []
            for row in result:
                row = list(row)
                if [row[1], row[2]] not in rest:
                    all_posts.append(row)
                    rest.append([row[1], row[2]])
            return all_posts

    def restaurants_find_address(self, rest_name):
        with self.connection:
            result = self.connection.execute(
                f"SELECT rest_address FROM restaurants WHERE rest_name LIKE '%{rest_name}%'").fetchone()
            return result[0]

    def restaurants_find_dish(self, rest_name, keyword):
        with self.connection:
            self.connection.execute("DROP TABLE IF EXISTS dish_fts")
            self.connection.execute("CREATE VIRTUAL TABLE dish_fts USING fts4(id, rest_name, rest_address, dish_name)")
            self.connection.execute("INSERT INTO dish_fts(id, rest_name, rest_address, dish_name) "
                                    "SELECT id, rest_name, rest_address, dish_name "
                                    "FROM restaurants")
            # self.connection.execute(f"SELECT * FROM dish_fts WHERE dish_name LIKE '%{keyword}%'")
            result = self.connection.execute(
                f"SELECT * FROM dish_fts WHERE rest_name = '{rest_name}' AND dish_name LIKE '%{keyword}%'").fetchall()
            return result

    def restaurants_get_all(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT id, rest_name, rest_address FROM restaurants").fetchall()
            all_posts = []
            rest = []
            for row in result:
                row = list(row)
                if [row[1], row[2]] not in rest:
                    all_posts.append(row)
                    rest.append([row[1], row[2]])
            return all_posts

    def restaurants_get_all_dish(self, rest_name):
        with self.connection:
            result = self.connection.execute(
                "SELECT id, rest_name, rest_address, dish_name FROM restaurants WHERE rest_name = ?",
                (rest_name,)).fetchall()
            return result

    def restaurants_get(self, restaurant) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM restaurants WHERE rest_name = ?",
                (restaurant,)).fetchall()
            return result

    # --- Взять рекомендации ---

    def restaurants_get_dish_rec_nutritionist(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_nutritionist FROM restaurants WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_community(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_community FROM restaurants WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_a_oblomov(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_a_oblomov FROM restaurants WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_a_ivlev(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_a_ivlev FROM restaurants WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish(self, restaurant, address, dish) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM restaurants WHERE rest_name = ? AND rest_address = ? AND dish_name = ?",
                (restaurant, address, dish)).fetchall()
            return result[0]

    def restaurants_get_by_id(self, id) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM restaurants WHERE id = ?",
                (id,)).fetchall()
            return result[0]

    def restaurants_get_by_name(self, restaurant: str, dish_name: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM restaurants WHERE rest_name = ? AND dish_name = ?",
                (restaurant, dish_name,)).fetchall()
            return result[0]

    # --- review ---

    def restaurants_set_review(self, id: int, review: str):
        review = review.lower()

        symbols_to_remove = ":;/<>"

        for symbol in symbols_to_remove:
            review = review.replace(symbol, "")

        reviews = self.restaurants_get_review(id) + " ; " + review

        with self.connection:
            self.cursor.execute(
                "UPDATE restaurants SET stat_reviews = ? WHERE id = ?",
                (reviews, id))

    def restaurants_get_review(self, id: int) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT stat_reviews FROM restaurants WHERE id = ?",
                (id,)).fetchall()
            return str(result[0][0])

    # --- rating ---

    def restaurants_set_rating(self, id: int, rating: int):

        ratings = self.restaurants_get_rating(id) + " ; " + str(rating)

        with self.connection:
            self.cursor.execute(
                "UPDATE restaurants SET stat_rating = ? WHERE id = ?",
                (ratings, id))

    def restaurants_get_rating(self, id: int) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT stat_rating FROM restaurants WHERE id = ?",
                (id,)).fetchall()
            return str(result[0][0])

    # ======================================================================================================================
    # ===== ТАБЛИЦА: recommendations =================================================================================================
    # ======================================================================================================================

    def recommendations_get_all(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM recommendations").fetchall()
            return result

    # ======================================================================================================================
    # ===== ТАБЛИЦА: waiters =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_waiter(self, user_id, user_rest, user_link, user_name=None, user_last_name=None, user_first_name=None,
                   user_surname=None, score="[]"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO waiters (waiter_id, waiter_rest, waiter_link, waiter_name, waiter_last_name,"
                " waiter_first_name, waiter_surname, waiter_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_rest, user_link, user_name, user_last_name, user_first_name, user_surname, score))

    def del_waiter(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM waiters WHERE waiter_id = ?",
                (user_id,))

    def check_waiter_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM waiters WHERE waiter_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_waiter_score(self, user_id: int, score: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE waiters SET waiter_score = ? WHERE waiter_id = ?",
                (score, user_id))

    def get_waiter_score(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT waiter_score FROM waiters WHERE waiter_id=?", (user_id,)).fetchall()
            return result[0][0]

    def get_waiters_waiters(self):
        with self.connection:
            result = self.connection.execute("SELECT waiter_id FROM waiters").fetchall()
            users_id = []
            for row in result:
                users_id.append(int(row[0]))
            return users_id

    def get_waiters_names_and_stats(self, rest):
        with self.connection:
            result = self.connection.execute("SELECT waiter_id, waiter_last_name, waiter_first_name, waiter_surname, "
                                             "waiter_score FROM waiters WHERE waiter_rest=?", (rest,)).fetchall()
            return result

    # ======================================================================================================================
    # ===== ТАБЛИЦА: baskets =================================================================================================
    # ======================================================================================================================

    def create_basket(self, user_id, basket="{}"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO baskets (user_id, basket) VALUES (?, ?)",
                (user_id, basket))

    def check_basket_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_basket(self, user_id, basket):
        with self.connection:
            self.cursor.execute(
                "UPDATE baskets SET basket = ? WHERE user_id = ?",
                (basket, user_id))

    def get_basket(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT basket FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            return result[0][0]

    def del_basket(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM baskets WHERE user_id = ?",
                (user_id,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: user_actions =================================================================================================
    # ======================================================================================================================

    def get_last_session(self, user_id):
        self.cursor.execute('''
            SELECT session_num, actions, start_time, end_time
            FROM user_actions
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT 1
        ''', (user_id,))
        result = self.cursor.fetchone()
        return result

    def create_new_session(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        SESSION_TIMEOUT = datetime.timedelta(hours=3)
        if last_session:
            last_session_num = last_session[0]
            last_start_time = datetime.datetime.strptime(last_session[2], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() - last_start_time > SESSION_TIMEOUT:
                new_session_num = last_session_num + 1
            else:
                new_session_num = last_session_num
        else:
            new_session_num = 1
        current_time = datetime.datetime.now().replace(microsecond=0)

        self.cursor.execute('''
            INSERT INTO user_actions (user_id, session_num, actions, start_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, new_session_num, action, current_time.strftime('%Y-%m-%d %H:%M:%S')))

    def update_session(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        if last_session:
            session_num, actions, start_time, end_time = last_session
            updated_actions = actions + '->' + action
            self.cursor.execute('''
                UPDATE user_actions
                SET actions = ?, end_time = ?
                WHERE user_id = ? AND session_num = ?
            ''', (updated_actions, datetime.datetime.now().replace(microsecond=0), user_id, session_num))

    def add_user_action(self, user_id, action):
        SESSION_TIMEOUT = datetime.timedelta(hours=3)
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        if last_session:
            last_start_time = datetime.datetime.strptime(last_session[2], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() - last_start_time > SESSION_TIMEOUT:
                self.create_new_session(user_id, action)
            else:
                self.update_session(user_id, action)
        else:
            self.create_new_session(user_id, action)

    def check_last_action(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            return False
        if not last_session:
            return False
        last_action = last_session[1].split('->')
        if last_action[-1] == action:
            return True

    # ======================================================================================================================
    # ===== ТАБЛИЦА: bosses =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_boss(self, user_id, user_rest):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO bosses (boss_id, boss_rest) VALUES (?, ?)",
                (user_id, user_rest))

    def del_boss(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM bosses WHERE boss_id = ?",
                (user_id,))

    def check_boss_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM bosses WHERE boss_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def get_boss_rest(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT boss_rest FROM bosses WHERE boss_id=?", (user_id,)).fetchall()
            return result[0][0]

    def set_boss_rest(self, user_id, user_rest):
        with self.connection:
            self.cursor.execute(
                "UPDATE bosses SET boss_rest = ? WHERE boss_id = ?",
                (user_rest, user_id))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: stop_lists =================================================================================================
    # ======================================================================================================================

    def create_stop_list(self, rest, stop_list="{}"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO stop_lists (rest, stop_list) VALUES (?, ?)",
                (rest, stop_list))

    def check_stop_list_exists(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM stop_lists WHERE rest=?", (rest,)).fetchall()
            return bool(len(result))

    def set_stop_list(self, rest, stop_list):
        with self.connection:
            self.cursor.execute(
                "UPDATE stop_lists SET stop_list = ? WHERE rest = ?",
                (stop_list, rest))

    def get_stop_list(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT stop_list FROM stop_lists WHERE rest=?", (rest,)).fetchall()
            return result[0][0]

    def del_stop_list(self, rest):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM stop_lists WHERE rest = ?",
                (rest,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: total_and_current_counts =================================================================================================
    # ======================================================================================================================

    def add_rest(self, rest, total_click_count=0, current_click_count=0, total_guests_count=0, current_guests_count=0):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO total_and_current_counts (rest, total_click_count, current_click_count, "
                "total_guests_count, current_guests_count) VALUES (?, ?, ?, ?, ?)",
                (rest, total_click_count, current_click_count, total_guests_count, current_guests_count))

    def check_rest_exists(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM total_and_current_counts WHERE rest=?", (rest,)).fetchall()
            return bool(len(result))

    def set_total_click_count(self, rest, total_click_count):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET total_click_count = ? WHERE rest = ?",
                (total_click_count, rest))

    def get_total_click_count(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT total_click_count FROM total_and_current_counts WHERE rest=?",
                                         (rest,)).fetchall()
            return result[0][0]

    def set_current_click_count(self, rest, current_click_count):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET current_click_count = ? WHERE rest = ?",
                (current_click_count, rest))

    def get_current_click_count(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT current_click_count FROM total_and_current_counts WHERE rest=?",
                                         (rest,)).fetchall()
            return result[0][0]

    def set_last_check_time(self, rest, time):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET last_check_time = ? WHERE rest = ?",
                (time, rest))

    def get_last_check_time(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT last_check_time FROM total_and_current_counts WHERE rest=?",
                                         (rest,)).fetchall()
            return result[0][0]

    def del_rest(self, rest):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM total_and_current_counts WHERE rest = ?",
                (rest,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: admins =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_admin(self, user_id, user_rest):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO admins (admin_id, temp_rest) VALUES (?, ?)",
                (user_id, user_rest))

    def del_admin(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM admins WHERE admin_id = ?",
                (user_id,))

    def check_admin_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM admins WHERE admin_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_admin_rest(self, user_id, rest):
        with self.connection:
            self.cursor.execute("UPDATE admins SET temp_rest = ? WHERE admin_id = ?", (rest, user_id,)).fetchall()

    def get_admin_rest(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT temp_rest FROM admins WHERE admin_id=?", (user_id,)).fetchall()
            return result[0][0]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: orders =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_order(self, user_id, user_rest, table_number, time):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO orders (waiter_id, rest, table_number, time) VALUES (?, ?, ?, ?)",
                (user_id, user_rest, table_number, time))

    def get_current_guests_count(self, rest):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        with self.connection:
            result = self.cursor.execute(f"SELECT time FROM orders WHERE rest=? AND time LIKE '%{current_time}%'",
                                         (rest,)).fetchall()
            if result:
                return len(result[0])
            else:
                return 0

    def get_current_waiter_guests(self, rest, waiter_id):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        with self.connection:
            result = self.cursor.execute(f"SELECT time FROM orders WHERE rest=? AND waiter_id=? AND time LIKE '%{current_time}%'",
                                         (rest, waiter_id,)).fetchall()
            if result:
                return len(result[0])
            else:
                return 0

# ======================================================================================================================
    # ===== ТАБЛИЦА: orders_history =================================================================================================
    # ======================================================================================================================



    def add_users_order(self, user_id, rest, basket):
        with self.connection:
            return self.cursor.execute("INSERT INTO orders_history (user_id, rest, basket) VALUES (?, ?, ?)", (user_id, rest, basket))

    def get_last_users_order(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT rest FROM orders_history WHERE user_id={user_id}").fetchall()
            return result[-1]


# ======================================================================================================================
# ===== ТАБЛИЦА: client_rest_search =================================================================================================
# ======================================================================================================================

    def add_search_filters(self, user_id, filters):
        with self.connection:
            return self.cursor.execute("INSERT INTO client_rest_search (id, filters) VALUES (?, ?)", (user_id, filters))

    def check_filters_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM client_rest_search WHERE id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_search_filters(self, user_id, filters):
        with self.connection:
            self.cursor.execute("UPDATE client_rest_search SET filters=? WHERE id=?", (filters, user_id,)).fetchall()

    def get_search_filters(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT filters FROM client_rest_search WHERE id=?", (user_id,)).fetchall()
            return result[0][0]