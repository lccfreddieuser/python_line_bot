# =====================================================================================================================================
# == import area ==
# =====================================================================================================================================

from flask import Flask,request , abort;
from linebot import( LineBotApi , WebhookHandler );
from linebot.exceptions import( InvalidSignatureError );
from linebot.models import *;
import requests;
import re;
import random;
import configparser;
import threading;
import time;
from bs4 import BeautifulSoup;
from imgurpython import ImgurClient;
                                                                         # ------------------------------------------------------------
from linebot.models.sources import SourceUser, SourceGroup, SourceRoom;  # <== for get event.source.userId but just a object ( > ___<)a
                                                                         # ------------------------------------------------------------

# =====================================================================================================================================
# == create server area ==
# =====================================================================================================================================

app = Flask(__name__)

# =====================================================================================================================================
# == create api ==
# =====================================================================================================================================

line_bot_api = LineBotApi('eFopGFnD4avYKx8aPo0XhFFBBBHirVeKNbVCFdpPRvmTv+XaQZskU9ErzEW0SqCrgdj888lutRej9tRcSccKI3pZY0pNM/Mu0NmjQEAeWnnnaa9FKynsyDt1L8x1OunC7a4BqAc5hztyU65brmusAgdB04t89/1O/w1cDnyilFU=')

# =====================================================================================================================================
# == create handler ==
# =====================================================================================================================================

handler = WebhookHandler('118f916ea3a3ce0aa0dfbb777f5441ed')

# =====================================================================================================================================
# == line_user init value ==
# =====================================================================================================================================

line_user = '';

# =====================================================================================================================================
# == 監聽所有來自 /callback 的 Post Request ==
# =====================================================================================================================================
# == app routing table will add this route ==
# =====================================================================================================================================
# == ex : app.route( '/index'  , method=['GET'] ) == USER 將會引導到我們網站的 "首    頁"
# == ex : app.route( '/search' , method=['GET'] ) == USER 將會引導到我們網站的 "搜尋頁面"
# == ex : print( 'app.__dict__[\'url_map\'] : {} \n'.format( app.__dict__['url_map'] );   # <=== print a app.__dict__['url_map'] object
# =====================================================================================================================================

# add route mapping
@app.route("/testing", methods=['POST'])
def test_method() : 
    return None;

@app.route("/callback", methods=['POST'])
def callback() : 

    # get line user id
    id = request.headers[ 'X-Request-Id' ];
    print( '*** ---- server player id : [{}]'.format( id ) );

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    print( 'server ::: body      ::: ' , body );           # <=== body is a object like < type 'dict' >
    print( 'server ::: signature ::: ' , signature );      # <=== signature is a encription text send by Line app server 

    app.logger.info("Request body: " + body)
    # handle webhook body

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'

# =====================================================================================================================================
# == 處理訊息 ( Flask self call method ) ==
# =====================================================================================================================================

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # ---------------------------------------------------------------------------------------------------------------------------------
    # step ( 0 ) prepare user [ msg ] , [ user_ID ]
    # ---------------------------------------------------------------------------------------------------------------------------------

    # event  :  {  
    #               "message"  : {  
    #                                "id": "10458863290325", 
    #                                "text": "aaaa", 
    #                                "type": "text"
    #                            }  ,  
    #               "replyToken": "8ee844948d9b42a0be955ae0a8b0520a", 
    #               "source": {
    #                             "type": "user", 
    #                             "userId": "U482f055b5200711b0e463e717db9dea8"
    #                         }  ,  
    #               "timestamp": 1566810045062, 
    #               "type": "message"
    #           }
    # 
    # https://github.com/line/line-bot-sdk-python

    # get msg form line cline user input < msg is never None or empty >
    msg = event.message.text;
    msg = msg.strip();

    # get user_ID from < user_ID is unique id from every line client user >
    event_str_obj =  str( event )
    s = event_str_obj.index( '"userId": "' ) + 11;
    e = event_str_obj.index( '"' , s );
    user_ID = event_str_obj[ s : e ];

    del event_str_obj;
    del s;
    del e;
    


    # ---------------------------------------------------------------------------------------------------------------------------------
    # step ( 1 ) use "user_ID" var login 
    # cmd[0] = [login]
    # ---------------------------------------------------------------------------------------------------------------------------------
    
    ck_1 = re.match( 'login' , msg );
    
    if( ck_1 and ( ck_1.span()[ 1 ] == len( msg ) ) ) : 
    
        print( '*** ---- server step 1 ================================== ' );
        print( '*** ---- server get msg           : [{}]'.format( msg     ) );
        print( '*** ---- server get userid        : [{}]'.format( user_ID ) );
    
        print( '*** ---- server get login process from user : [{}]'.format( user_ID ) );
        ck_2 = sign_in( user_ID );
    
        if( not ck_2 ) : 
    
            # none this user -----------------------------------------------------------------------------
            sign_up( user_ID , SourceUser );
            add_cmd( user_ID , 'login' );
            help = '\n\nPlease type [ help ] to pup user menu !'
            message = TextSendMessage( text=( 'login successful ! Hi , dear user ! Wellcom to my service !' + help ) );
            del help;
            line_bot_api.reply_message( event.reply_token , message );
            return;
    
        # prepare this user succressful ------------------------------------------------------------------
        add_cmd( user_ID , 'login' );
        create_ans( user_ID );
        help = '\n\nPlease type [ help ] to pup user menu !'
        message = TextSendMessage( text=( 'login successful ! Hi , dear user ! Long time no see !' + help ) );
        del help;
        line_bot_api.reply_message( event.reply_token , message );
        return;



    # ---------------------------------------------------------------------------------------------------------------------------------
    # step ( 2 ) use "user_ID" var logout
    # ---------------------------------------------------------------------------------------------------------------------------------
   
    ck_1 = re.match( 'logout' , msg );
    
    if( ck_1 and ( ck_1.span()[ 1 ] == len( msg ) ) ) : 

        print( '*** ---- server step 2 ================================== ' );
        print( '*** ---- server get msg           : [{}]'.format( msg     ) );
        print( '*** ---- server get userid        : [{}]'.format( user_ID ) );

        print( '*** ---- server get logout process from user : [{}]'.format( user_ID ) );
        txt = sign_out( user_ID );
        message = TextSendMessage( text=( txt ) );
        del txt;
        line_bot_api.reply_message( event.reply_token , message );

        return;



    # ---------------------------------------------------------------------------------------------------------------------------------
    # step ( 3 ) useing service
    # ---------------------------------------------------------------------------------------------------------------------------------

    try : 

        level = { 'play':1 , 'search':1 , 'help':1 , 'password':2 , 'game2':2 , 'game3':2 , 'google':3 , 'yahoo':3 , 'books':3 , };
        # books  = 'https://search.books.com.tw/search/query/key/' + key + '/cat/all';
        # google = 'https://www.google.com/search?q=' + key + '&tbm=bks'
        # yahoo  = 'https://tw.search.yahoo.com/search?p=' + key '&fr2=sb-top-tw.shopping.search'
      
        print( '*** ---- server step 3 ================================== ' );
        print( '*** ---- server get msg           : [{}]'.format( msg     ) );
        print( '*** ---- server get userid        : [{}]'.format( user_ID ) );

        # has this user  -----------------------------------------------------------------------------
        current_user = get_user( user_ID );
        if( current_user == None ) : 
            raise None_This_User_Exception('');
            pass;

        # write cmd[1]

        if( msg in level ) : 

            l = level.get( msg );
            if( len( current_user.cmd ) == l ) : 
                current_user.cmd.append( '' );
            pass;
            current_user.cmd[ l ] = msg;
            current_user.cmd = current_user.cmd[ 0 : ( level.get( msg ) + 1 ) : 1 ]
            print( '*** ---- server step 3.1 ================================== ' );
            print( '*** ---- list server cmd : [{}] , from this user : [{}]'.format( get_user( user_ID ).cmd , user_ID ) );

        else : 
            
            obj = re.match( '[\d]{1,}' , msg );

            if( obj == None ) : 
            
                # error cmd append error -----------------------------------------------------------------------------
                print( 'server - - can not append this cmd Exception $$$ ' + msg )
                message = TextSendMessage( text=( 'input cmd {} error , please re check !'.format( msg ) ) );
                del obj;
                line_bot_api.reply_message( event.reply_token , message );
                return;

            elif( obj != None and ( obj.span()[ 1 ] == len( msg ) ) ) : 

                if( int( msg ) > 99 or int( msg ) < 1 ) : 
                    # cmd range error -----------------------------------------------------------------------------
                    print( 'server - - can not append this cmd Exception $$$ range error $$$' + str( msg ) )
                    message = TextSendMessage( text=( 'input range {} error , please re check !'.format( msg ) ) );
                    del obj;
                    line_bot_api.reply_message( event.reply_token , message );
                    return;

                current_user.cmd.append( str( msg ) );
                del obj;
                print( '*** ---- server step 3.1 ================================== ' );
                print( '*** ---- list server cmd : [{}] , from this user : [{}]'.format( get_user( user_ID ).cmd , user_ID ) );
                pass;

            pass;

        # last_cmd  -----------------------------------------------------------------------------
        last_cmd = get_last_cmd( user_ID );

        # cmd list -----------------------------------------------------------------------------
        cmd_list = get_cmd_from_this( user_ID , 1 );

        # service here

        if( last_cmd == 'help' ) : 
            raise None_This_Cmd_Exception('');
            return;

        if( last_cmd == 'play' ) : 
            print( '*** ---- server step 3.4 ================================== ' );
            print( '*** ---- server get play process from user : [{}]'.format( user_ID ) );
            txt  =   'please select a game [ password ] | [ game2 ] | [ game3 ] to play !'
            txt += '\nenjoy your game THX !'
            message = TextSendMessage( text=( txt ) );
            del txt;
            line_bot_api.reply_message( event.reply_token , message );
            return;

        if( last_cmd == 'search' ) : 
            print( '*** ---- server step 3.5 ================================== ' );
            print( '*** ---- server get search process from user : [{}]'.format( user_ID ) );
            message = TextSendMessage( text=( 'you are searching !' ) );
            line_bot_api.reply_message( event.reply_token , message );
            return;
            pass;

        if( check_cmd( cmd_list , ( 'play,password,' + '(' + '[\d]{1,}' + '([*]la){0,1}' + '([*]le){0,1}' + '[,]' ')*' + '(' + '[\d]{1,}' + '([*]la){0,1}' + '([*]le){0,1}' + '){1}' ) ) ) : 
            print( '*** ---- server get [ playing password ] process from user : [{}]'.format( user_ID ) );

            # play,password,50 process 

            try : 
                num = int( msg );
                print( '*** ---- server playing user input : [{}]'.format( num ) );
                print( '*** ---- server playing user ans   : [{}]'.format( current_user.get_ans() ) );
                pass;
      
            except : 
                print( '$$$ ---- server get user input number type error : [ ' + str( num ) + ' ]' );
                message = TextSendMessage( text=( 'Error ! input type error please type a number !' ) );
                line_bot_api.reply_message( event.reply_token , message );
                return;
 
            sp = current_user.min_num;
            ep = current_user.max_num;
            during = '';

            # too large :: 
            if( num > current_user.get_ans() ) : 
                current_user.cmd[ -1 ] = current_user.cmd[ -1 ] + '*la';
                text = 'too large , please guess lesser !';
                if( len( current_user.cmd ) == 3 ) : 
                    sp = current_user.min_num;
                    pass;
                else : 
                    for i in current_user.cmd[ -1 : : -1 ] : 
                        if( '*le' in i ) : 
                            sp = i[ 0 : i.index( '*' ) : 1 ];
                            print( '$$$ server write new sp [{}]'.format( sp ) );
                            break;
                        pass;
                ep = num;
                print( '$$$ server write old ep [{}]'.format( ep ) );
              
            # too less :: 
            elif( num < current_user.get_ans() ) : 
                current_user.cmd[ -1 ] = current_user.cmd[ -1 ] + '*le';
                text = 'too less , please guess larger !';
                # first guess len( cmd == 3 ) 
                if( len( current_user.cmd ) == 3 ) : 
                    ep = current_user.max_num;
                    pass;
                else : 
                    for i in current_user.cmd[ -1 : : -1 ] : 
                        if( '*la' in i ) : 
                            ep = i[ 0 : i.index( '*' ) : 1 ];
                            print( '$$$ server write new ep [{}]'.format( ep ) );
                            break;
                        pass;
                sp = num;
                print( '$$$ server write old sp [{}]'.format( sp ) );
                  
            elif( num == current_user.get_ans() ) : 
                text = 'Bingo !;'
                current_user.is_win();
                  
            if( current_user.check_win() ) : 
                current_user.init();
                current_user.uscore += 10;
                create_ans( user_ID );
                print( 'W. replay status : ' , 'user win this game ! score : ' + str( current_user.uscore ) );
                print( 'W. replay status : ' , 'this game will auto restart !' );
                message = TextSendMessage( text=( 'you win  ! score : ' + str( current_user.uscore ) ) );
                del during;
                del sp;
                del ep;
                line_bot_api.reply_message( event.reply_token , message );
                return;
      
            else :
                during = '[ {} ~ {} ]'.format( sp , ep )
                print( 'C. replay status : ' , 'user turn status : ' + text + ' ??? ' + current_user.cmd[ -1 ] );
                message = TextSendMessage( text=( ( 'your turn status {} ! ' + text + ' guess during {} !' ).format( num , during ) ) );
                del during;
                del sp;
                del ep;
                line_bot_api.reply_message( event.reply_token , message );
                return;

            # txt  =   'user playing password game !'
            # message = TextSendMessage( text=( txt ) );
            # del txt;
            # line_bot_api.reply_message( event.reply_token , message );
            return;

        if( check_cmd( cmd_list , 'play,password' ) ) : 
            current_user.init();
            print( '*** ---- server step 3.4.1 ================================== ' );
            print( '*** ---- server get play password process from user : [{}]'.format( user_ID ) );
            txt  =   'this password during [ 0 - 100 ] , please type a number to play !'
            message = TextSendMessage( text=( txt ) );
            del txt;
            line_bot_api.reply_message( event.reply_token , message );
            return;

        if( check_cmd( cmd_list , 'play,game2' ) ) : 
            current_user.init();
            print( '*** ---- server step 3.4.2 ================================== ' );
            print( '*** ---- server get play game2 process from user : [{}]'.format( user_ID ) );
            txt  =   'Stay tuned for the new game2 !'
            message = TextSendMessage( text=( txt ) );
            del txt;
            line_bot_api.reply_message( event.reply_token , message );
            return;

        if( check_cmd( cmd_list , 'play,game3' ) ) : 
            current_user.init();
            print( '*** ---- server step 3.4.4 ================================== ' );
            print( '*** ---- server get play game3 process from user : [{}]'.format( user_ID ) );
            txt  =   'Stay tuned for the new game3 !'
            message = TextSendMessage( text=( txt ) );
            del txt;
            line_bot_api.reply_message( event.reply_token , message );
            return;

        # ===============================================================================================================================
        # ===============================================================================================================================
        # ===============================================================================================================================
        # ===============================================================================================================================
        # ===============================================================================================================================
        # ===============================================================================================================================

        # none this cmd  -----------------------------------------------------------------------------
        raise None_This_Cmd_Exception('');
      
        pass; # end if --------------------------
      
    except None_This_User_Exception : 

        print( '*** ---- server step 3.2 ================================== ' );
        print( 'server - - get None_This_User_Exception :: ' )
        help  =   'please login at first !           ' + '\n';
        help +=   'type [ login ] .                  ' + '\n';
        help += '\nif you are not my account , system will sign up auto';
        message = TextSendMessage( text=( help ) );
        del help;
        del current_user;
        line_bot_api.reply_message( event.reply_token , message );

        return;

    except None_This_Cmd_Exception : 

        print( '*** ---- server step 3.3 ================================== ' );
        print( '*** ---- server get help process from user : [{}]'.format( user_ID ) );
        help  = 'service help list -----------------  ' + '\n';
        help += '\n1. please type [ login ]           ' + '\n';
        help +=   '   to sign in or sign up !         ' + '\n';
        help += '\n2. after login , please type       ' + '\n';
        help +=   '   [ play ] or                     ' + '\n';
        help +=   '   [ search ]                      ' + '\n';
        help +=   '   to use service !                ' + '\n';
        help += '\n3. after play , please type num !  ' + '\n';
        help += '     enjoy your game !               ' + '\n';
        help += '\n4. after search , please type key !' + '\n';
        message = TextSendMessage( text=( help ) );
        del help;
        del current_user;
        line_bot_api.reply_message( event.reply_token , message );

        return;

    except Exception as err : 
      
        # show app.py code error here -----------------------------------------------------------------------------
        print( 'server - - code Exception $$$ ' + str( err ) )
        del err;

        return; # end except --------------------------
      
    # ---------------------------------------------------------------------------------------------------------------------------------

    pass; # end method handle_message

    
# =====================================================================================================================================
# == method for server init step ==
# =====================================================================================================================================

def server_init() : 

    print( 'server start del local var ! ' );

    if ( 'static_store' in locals() ) : 
        del static_store;
        print( 'server del local var [ static_store ]' );
        pass;
    
    if ( 'user' in locals() ) : 
        del user;
        print( 'server del local var [ user ]' );
        pass;

    if ( 'static' in locals() ) : 
        del static;
        print( 'server del local var [ static ]' );
        pass;
    
    if ( 'line_user' in locals() ) : 
        del line_user;
        print( 'server del local var [ line_user ]' );
        pass;
    
    if ( 'find_user' in locals() ) : 
        del find_user;
        print( 'server del local var [ find_user ]' );
        pass;
    
    if ( 'get_user' in locals() ) : 
        del get_user;
        print( 'server del local var [ get_user ]' );
        pass;

    if ( 'temp_user' in locals() ) : 
        del temp_user;
        print( 'server del local var [ temp_user ]' );
        pass;

    if ( 'ans' in locals() ) : 
        del ans;
        print( 'server del local var [ ans ]' );
        pass;

    pass;

def server_check_all_status() : 

    global ans;

    print( '\n===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== server checking ... 1. static store : ' , static );
    print( '===== server checking ... 2. temp_user    : ' , temp_user );
    print( '===== server checking ... 3. init ans     : ' , ans );

    create_ans();
    print( '===== server checking ... 4. create_ans   : ' , ans );
    ans = -1;

    print( '===== server checking ... 5. test find_user( \'temp_user_name\' ) ' , find_user( 'temp_user_name' ) );
    print( '===== server checking ... 6. test get_user( \'temp_user_name\') '   , get_user(  'temp_user_name' ) );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== \n' );

    pass;

# =====================================================================================================================================
# == class for server need ==
# =====================================================================================================================================

class None_This_User_Exception( Exception ) : 
    pass;

class None_This_Cmd_Exception( Exception ) : 
    pass;

class static_store() : 
    
    def __init__( self ) : 
        print( 'server prepare static_store ... ing ! ' );
        self.user   = [];
        pass;
    
    pass;

class user() : 
    
    def __init__( self , name=None , SourceUser=None )  : 
        print( 'creating user : ' + name );
        self.uname            = name;
        # self.source_user      = SourceUser;
        self.uscore           = 0;
        self.win              = False;
        # self.start            = False;
        self.ans              = -1;
        self.cmd              = [];
        self.pushed           = False;
        self.min_num          = 0;
        self.max_num          = 100;
        pass;
    
    # def start_game( self ) : 
    #     self.start = True;
    #     pass;
    
    def toString( self ) : 
        return ( '>> ' + self.uname + ' : ' + str( self.uscore ) );
    
    def check_win( self ) : 
        return self.win;
    
    def is_win( self ) : 
        self.win = True;
    
    # def check_start( self ) : 
    #     return self.start;

    def init( self ) : 
        self.win = False;
        pass;

    def get_name( self ) : 
        return self.uname;

    def set_ans( self , ans ) : 
        self.ans = ans;

    def get_ans( self ) : 
        return self.ans;

    pass;

# =====================================================================================================================================
# == method for server need ==
# =====================================================================================================================================

def sign_in( name ) : 
    if( not find_user( name ) ) : 
        return False;
    return True

def sign_out( name ) : 
    if( find_user( name ) ) : 
        static.user.remove( get_user( name ) );
        return 'user logout successful !';
    else : 
        return 'none this user to logout . Or you are already logout , can not do it again !';

def sign_up( name , SourceUser ) : 
    c_user = user( name , SourceUser );
    static.user.append( c_user );
    print(   '1. server get a new user : ' , c_user.toString() );
    print(   '#. server total user : ' , len( static.user ) );
    print( '\n#. -------------------------------------------------------------- ' );
    for i in static.user : 
        print( '#. all user : ' , i );
        pass;
    print(   '#. -------------------------------------------------------------- \n\n' );
    create_ans( name );
    del c_user;
    return True;

def create_ans( name=None ) : 
    import random;
    global ans;
    ans = random.randint( 1 , 100 );
    print( '===== >>> server create random ans : [{}]'.format( ans ) );
    if( name != None ) : 
        get_user( name ).set_ans( ans );
        print( '*** ---- server set this ans : [{}] , into user : [{}]'.format( ans , name ) );
        pass;
    pass;

def find_user( user_name ) : 
    for i in static.user : 
        if( i.uname == user_name ) : 
            return True;
        pass;
    return False;

def get_user( user_name ) : 
    for i in static.user : 
        if( i.uname == user_name ) : 
            return i;
        pass;
    return None;

def add_cmd( user_ID , cmd ) : 
    list_cmd = get_user( user_ID ).cmd;
    if( not cmd in list_cmd ) : 
        list_cmd.append( cmd );
        pass;
    del list_cmd;
    print( '*** ---- list server cmd : [{}] , from this user : [{}]'.format( get_user( user_ID ).cmd , user_ID ) );
    return True;

def get_last_cmd( user_ID ) : 
    txt = None;
    obj = get_user( user_ID );
    if( obj != None ) : 
        txt = obj.cmd[ -1 ];
        pass;
    del obj;
    return txt;

def get_cmd_from_this( user_ID , num ) : 

    obj = get_user( user_ID ).cmd;

    return obj[ num : : 1 ];

def check_cmd( cmd_list , str_a ) : 

    str_b = ','.join( cmd_list );

    print( 'in server === str_b : [{}]'.format( str_b ) );

    obj = re.match( str_a , str_b );
    if( obj and ( obj.span()[ 1 ] == len( str_b ) ) ) : 
        return True;
    
    del obj;
    return False;

def send_pushmsg( help ) : 

    from time import sleep;

    users = static.user;

    print( '=== server pushmsg is rinning - - - ' );

    while( True ) : 

        sleep( 1 );

        print( '===== server pushmsg is rinning - - - ' );

        for i in users : 

            if( not i.pushed ) : 
                # print( '@@@ server pushmsg a msg to the user [{}] - - - '.format( i.uname ) );
                # line_bot_api.push_message( i.uname , TextSendMessage( text=help ) );
                # i.pushed = True;
                # to is need JSON serializable ( just need "line user id" )
                pass;

        # break;

        pass;

    pass;

# =====================================================================================================================================
# == server running here ==
# =====================================================================================================================================

import os

if __name__=="__main__":

    print( '\n===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( 'app.__dict__[\'url_map\'] : ' , app.__dict__['url_map'] );  # <== print all app routting table
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ' );
    print( '===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== \n' );

    # server init
    server_init();

    # set all server var for need
    static = static_store();
    temp_user = user( 'temp_user_name' )
    static.user.append( temp_user );
    ans = -1;

    # check server all status ifis prepared
    server_check_all_status();

    # del temp var
    static.user.remove( temp_user );
    del temp_user;

    # https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/
    # python threading

    # 執行該子執行緒
    help  = '1. [login]  to login                  :';
    help += '2. [logout] to logout                 :';
    help += '3. [play]   to play game              :';
    help += '4. [search] to search key from google :';
    # t = threading.Thread( target=send_pushmsg( help ) );
    # t.start();

    port=int(os.environ.get('PORT',5000));
    app.run(host='0.0.0.0',port=port);
    pass;

# =====================================================================================================================================
