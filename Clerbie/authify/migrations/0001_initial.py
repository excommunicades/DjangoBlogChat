# Generated by Django 5.1.4 on 2025-01-16 19:26

import authify.models
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clerbie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=30)),
                ('nickname', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('avatar', models.ImageField(default='default/default_avatar.png', upload_to=authify.models.image_upload_function)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('role', models.CharField(choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Administrator')], default='user', max_length=10)),
                ('behavior_points', models.IntegerField(default=1000)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='other', max_length=6)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('country', models.CharField(choices=[('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BR', 'Brazil'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('CV', 'Cabo Verde'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo (Democratic Republic of the)'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', 'Korea (North)'), ('KR', 'Korea (South)'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'North Macedonia'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn Islands'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Réunion'), ('RO', 'Romania'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('BL', 'Saint Barthélemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syria'), ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VA', 'Vatican City'), ('VE', 'Venezuela'), ('VN', 'Vietnam'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], default='None')),
                ('time_zones', models.CharField(choices=[('UTC-12:00', 'UTC-12:00'), ('UTC-11:00', 'UTC-11:00'), ('UTC-10:00', 'UTC-10:00'), ('UTC-09:00', 'UTC-09:00'), ('UTC-08:00', 'UTC-08:00'), ('UTC-07:00', 'UTC-07:00'), ('UTC-06:00', 'UTC-06:00'), ('UTC-05:00', 'UTC-05:00'), ('UTC-04:00', 'UTC-04:00'), ('UTC-03:00', 'UTC-03:00'), ('UTC-02:00', 'UTC-02:00'), ('UTC-01:00', 'UTC-01:00'), ('UTC+00:00', 'UTC+00:00'), ('UTC+01:00', 'UTC+01:00'), ('UTC+02:00', 'UTC+02:00'), ('UTC+03:00', 'UTC+03:00'), ('UTC+04:00', 'UTC+04:00'), ('UTC+05:00', 'UTC+05:00'), ('UTC+06:00', 'UTC+06:00'), ('UTC+07:00', 'UTC+07:00'), ('UTC+08:00', 'UTC+08:00'), ('UTC+09:00', 'UTC+09:00'), ('UTC+10:00', 'UTC+10:00'), ('UTC+11:00', 'UTC+11:00'), ('UTC+12:00', 'UTC+12:00')], default='UTC+00:00')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('BLOCKED', 'Blocked')], default='ACTIVE', max_length=10)),
                ('telegram', models.CharField(blank=True, max_length=100, null=True)),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('github', models.URLField(blank=True, null=True)),
                ('instagram', models.CharField(blank=True, max_length=100, null=True)),
                ('skype', models.CharField(blank=True, max_length=100, null=True)),
                ('discord', models.CharField(blank=True, max_length=100, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('youtube', models.URLField(blank=True, null=True)),
                ('business_email', models.EmailField(blank=True, max_length=100, null=True)),
                ('job_title', models.CharField(blank=True, choices=[('PYTHON_BACKEND', 'Python Backend Developer'), ('JAVA_BACKEND', 'Java Backend Developer'), ('NODEJS_BACKEND', 'Node.js Backend Developer'), ('PHP_BACKEND', 'PHP Backend Developer'), ('RUBY_BACKEND', 'Ruby Backend Developer'), ('GO_BACKEND', 'Go Backend Developer'), ('C_SHARP_BACKEND', 'C# Backend Developer'), ('CPLUSPLUS_BACKEND', 'C++ Backend Developer'), ('JAVASCRIPT_FRONTEND', 'JavaScript Frontend Developer'), ('REACT_FRONTEND', 'React Frontend Developer'), ('ANGULAR_FRONTEND', 'Angular Frontend Developer'), ('VUE_FRONTEND', 'Vue.js Frontend Developer'), ('SASS_CSS_FRONTEND', 'SASS/CSS Frontend Developer'), ('JQUERY_FRONTEND', 'jQuery Frontend Developer'), ('TYPESCRIPT_FRONTEND', 'TypeScript Frontend Developer'), ('NEXTJS_FRONTEND', 'Next.js Frontend Developer'), ('FULLSTACK', 'Fullstack Developer'), ('PYTHON_FULLSTACK', 'Python Fullstack Developer'), ('JAVASCRIPT_FULLSTACK', 'JavaScript Fullstack Developer'), ('JAVA_FULLSTACK', 'Java Fullstack Developer'), ('MOBILE_ANDROID', 'Android Developer'), ('MOBILE_IOS', 'iOS Developer'), ('MOBILE_FLUTTER', 'Flutter Developer'), ('MOBILE_REACT_NATIVE', 'React Native Developer'), ('MOBILE_XAMARIN', 'Xamarin Developer'), ('MOBILE_KOTLIN', 'Kotlin Developer'), ('DEVOPS', 'DevOps Engineer'), ('CLOUD_ENGINEER', 'Cloud Engineer'), ('CLOUD_ARCHITECT', 'Cloud Architect'), ('KUBERNETES_ENGINEER', 'Kubernetes Engineer'), ('AWS_ENGINEER', 'AWS Engineer'), ('AZURE_ENGINEER', 'Azure Engineer'), ('GCP_ENGINEER', 'Google Cloud Engineer'), ('DATA_SCIENTIST', 'Data Scientist'), ('MACHINE_LEARNING_ENGINEER', 'Machine Learning Engineer'), ('DATA_ENGINEER', 'Data Engineer'), ('AI_ENGINEER', 'AI Engineer'), ('DATA_ANALYST', 'Data Analyst'), ('BUSINESS_INTELLIGENCE_ANALYST', 'Business Intelligence Analyst'), ('DEEP_LEARNING_ENGINEER', 'Deep Learning Engineer'), ('DATA_VISUALIZATION_ENGINEER', 'Data Visualization Engineer'), ('STATISTICIAN', 'Statistician'), ('GAME_DEV', 'Game Developer'), ('UNITY_GAME_DEV', 'Unity Game Developer'), ('UNREAL_ENGINE_GAME_DEV', 'Unreal Engine Game Developer'), ('GAMES_DEVELOPER_2D', '2D Game Developer'), ('GAMES_DEVELOPER_3D', '3D Game Developer'), ('MOBILE_GAME_DEV', 'Mobile Game Developer'), ('UI_DESIGNER', 'UI Designer'), ('UX_DESIGNER', 'UX Designer'), ('UI_UX_DEVELOPER', 'UI/UX Developer'), ('UX_RESEARCHER', 'UX Researcher'), ('VISUAL_DESIGNER', 'Visual Designer'), ('INTERACTION_DESIGNER', 'Interaction Designer'), ('MOTION_DESIGNER', 'Motion Designer'), ('GRAPHIC_DESIGNER', 'Graphic Designer'), ('QA_ENGINEER', 'Quality Assurance Engineer'), ('AUTOMATION_TESTER', 'Automation Tester'), ('MANUAL_TESTER', 'Manual Tester'), ('PERFORMANCE_TESTER', 'Performance Tester'), ('SECURITY_TESTER', 'Security Tester'), ('LOAD_TESTER', 'Load Tester'), ('TEST_AUTOMATION_ENGINEER', 'Test Automation Engineer'), ('SECURITY_ENGINEER', 'Security Engineer'), ('CISO', 'Chief Information Security Officer'), ('PENETRATION_TESTER', 'Penetration Tester'), ('SECURITY_ANALYST', 'Security Analyst'), ('NETWORK_SECURITY_ENGINEER', 'Network Security Engineer'), ('MOBILE_SECURITY_ENGINEER', 'Mobile Security Engineer'), ('APPLICATION_SECURITY_ENGINEER', 'Application Security Engineer'), ('COMPLIANCE_ENGINEER', 'Compliance Engineer'), ('SYSTEM_ADMIN', 'System Administrator'), ('LINUX_ADMIN', 'Linux Administrator'), ('WINDOWS_ADMIN', 'Windows Administrator'), ('NETWORK_ENGINEER', 'Network Engineer'), ('NETWORK_ADMIN', 'Network Administrator'), ('CISCO_ENGINEER', 'Cisco Engineer'), ('UNIX_ADMIN', 'Unix Administrator'), ('BLOCKCHAIN_DEVELOPER', 'Blockchain Developer'), ('SMART_CONTRACT_DEVELOPER', 'Smart Contract Developer'), ('CRYPTO_DEVELOPER', 'Cryptocurrency Developer'), ('SOLIDITY_DEVELOPER', 'Solidity Developer'), ('DECENTRALIZED_APP_DEVELOPER', 'Decentralized Application Developer'), ('SCRUM_MASTER', 'Scrum Master'), ('PROJECT_MANAGER', 'Project Manager'), ('PRODUCT_OWNER', 'Product Owner'), ('TECH_LEAD', 'Technical Lead'), ('SOFTWARE_ARCHITECT', 'Software Architect'), ('CTO', 'Chief Technology Officer'), ('CPO', 'Chief Product Officer'), ('AR_DEVELOPER', 'Augmented Reality Developer'), ('VR_DEVELOPER', 'Virtual Reality Developer'), ('AR_VR_DEVELOPER', 'AR/VR Developer'), ('IOT_DEVELOPER', 'IoT Developer'), ('IOT_ENGINEER', 'IoT Engineer'), ('ROBOTICS_ENGINEER', 'Robotics Engineer'), ('NLP_ENGINEER', 'Natural Language Processing Engineer'), ('COMPUTER_VISION_ENGINEER', 'Computer Vision Engineer'), ('ROBOTICS_DEVELOPER', 'Robotics Developer'), ('TECHNICAL_WRITER', 'Technical Writer'), ('IT_SUPPORT', 'IT Support'), ('IT_CONSULTANT', 'IT Consultant'), ('SALES_ENGINEER', 'Sales Engineer'), ('BUSINESS_ANALYST', 'Business Analyst'), ('RESEARCHER', 'Researcher'), ('MARKETING_SPECIALIST', 'Marketing Specialist'), ('SEO_SPECIALIST', 'SEO Specialist'), ('SOCIAL_MEDIA_MANAGER', 'Social Media Manager'), ('CUSTOMER_SUPPORT', 'Customer Support'), ('TRAINER', 'IT Trainer'), ('DOCUMENTATION_ENGINEER', 'Documentation Engineer'), ('LEGAL_ENGINEER', 'Legal Engineer')], default='None', max_length=40, null=True)),
                ('two_factor_method', models.CharField(blank=True, choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')], default='disabled', max_length=50, null=True)),
                ('last_activity', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'UserProfile',
            },
        ),
    ]