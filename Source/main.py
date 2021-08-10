import utils.database
import model.baiviet


def clean():
    utils.database.close_connection()

def main():
    conn = utils.database.create_connection()

    if conn is not None:
        if not utils.database.create_schema():
            print("Init database error")
            return clean()

        model.baiviet.add_bai_viet()
        model.baiviet.get_bai_viet()



if __name__ == '__main__':
    main()