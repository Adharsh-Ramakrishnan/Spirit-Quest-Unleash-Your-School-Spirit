class get_user_details():
    def __init__(self):
        self.first_name = self.logged_in_user_details[0][1]
        self.last_name = self.logged_in_user_details[0][2]
        self.date_of_birth = self.logged_in_user_details[0][8]
        self.user_gender = self.logged_in_user_details[0][16]
        self.grade = self.logged_in_user_details[0][7]
        self.events_attended = self.logged_in_user_details[0][10]
        self.user_points = self.logged_in_user_details[0][11]
        self.user_profile_picture = self.logged_in_user_details[0][12]
        self.emergency_contact_name = self.logged_in_user_details[0][13]
        self.emergency_contact_phone = self.logged_in_user_details[0][14]
        self.emergency_contact_email = self.logged_in_user_details[0][15]

        return get_user_details
