from flask import Flask, flash, request, jsonify
from con import set_connection
from loggerinstance import logger
import json

app = Flask(__name__)


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as e:
            conn = kwargs.get('conn')
            if conn:
                conn.rollback()
            logger.error(str(e))
            return jsonify({"error": "Database error"})
        except Exception as e:
            logger.error(str(e))
            return jsonify({"error": "Internal server error"})
        finally:
            conn = kwargs.get('conn')
            cur = kwargs.get('cur')
            if cur:
                cur.close()
            if conn:
                conn.close()

    return wrapper


@app.route('/v1/create', methods=['POST'])
@handle_exceptions
def create_profile():
    """ Creates the profile for the given name and description and inserts it into database"""
    # {"name": "bhanu",
    #  "description": "Bhanu profile for instagram"
    #  }

    data = request.json
    name = date.get['name']
    description = data.get['description']

    cur, conn = set_connection()
    cur.execute("INSERT INTO profiles (name, description) VALUES (%s, %s)", (name, description))
    conn.commit()

    logger.info("Profile created successfully")
    return {"message": "Profile created successfully"}, 201


# Retrieve a list of all profiles from the database
@app.route('/v1/get_profiles', methods=['GET'], endpoint='get_profiles')
@handle_exceptions
def get_profiles():
    """ returns all the profiles"""
    cur, conn = set_connection()
    cur.execute("SELECT * FROM profiles")
    rows = cur.fetchall()

    logger.info("Retrieved profiles successfully")
    return jsonify(rows), 200


# Create a new post for a profile in the database
@app.route('/v1/<int:profile_id>/create_post', methods=['POST'], endpoint='create_post')
@handle_exceptions
def create_post(profile_id):
    """Creates a post for the given profile_id"""
    # {
    #     "content": "Weekend vibes"
    # }

    content = request.json['content']

    cur, conn = set_connection()
    cur.execute("INSERT INTO posts (profile_id, content) VALUES (%s, %s)", (profile_id, content))
    conn.commit()

    logger.info("Post created successfully")
    return {"message": "Post created successfully"}, 201


# Retrieve a list of all posts for a profile from

@app.route('/v1/<int:profile_id>/', methods=['GET'], endpoint='get_posts')
@handle_exceptions
def get_posts(profile_id):
    """Lists all the posts for a given profile_id"""
    cur, conn = set_connection()
    cur.execute("SELECT * FROM posts WHERE profile_id = %s", (profile_id,))
    rows = cur.fetchall()

    logger.debug(f"Retrieved {len(rows)} posts for profile_id {profile_id}")
    return jsonify(rows), 200


@app.route('/v1/<int:post_id>/like', methods=['PUT'], endpoint='like_post')
@handle_exceptions
def like_post(post_id):
    """Updates the like count for a given post"""
    cur, conn = set_connection()
    cur.execute("UPDATE posts SET like_count = like_count + 1 WHERE id = %s", (post_id,))
    conn.commit()

    logger.debug(f"Liked post with id {post_id}")
    return {"message": "Post liked successfully"}, 200


@app.route('/v1/<int:post_id>/comment', methods=['POST'], endpoint='create_comment')
@handle_exceptions
def create_comment(post_id):
    content = request.json.get('content')
    cur, conn = set_connection()
    logger.debug(f"Creating comment for post with id {post_id}")

    cur.execute("INSERT INTO comments (post_id, content) VALUES (%s, %s)",
                (post_id, content))
    cur.execute("UPDATE posts SET comment_count = comment_count+1 WHERE id = %s", (post_id,))
    conn.commit()
    logger.debug(f"Created comment for post with id {post_id}")
    return {"message": "Comment created successfully"}, 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
