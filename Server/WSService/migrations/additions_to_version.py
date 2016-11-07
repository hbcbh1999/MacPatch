from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
	### Add MacPatch VIEWS ###
    qstr = ''' CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `mp_clients_view` AS
    select `mp_clients`.`cuuid` AS `cuuid`,`mp_clients`.`serialno` AS `serialNo`,
    `mp_clients`.`hostname` AS `hostname`,`mp_clients`.`computername` AS `computername`,
    `mp_clients`.`ipaddr` AS `ipaddr`,`mp_clients`.`macaddr` AS `macaddr`,`mp_clients`.`osver` AS `osver`,
    `mp_clients`.`ostype` AS `ostype`,`mp_clients`.`consoleuser` AS `consoleUser`,
    `mp_clients`.`needsreboot` AS `needsreboot`,`mp_clients`.`agent_version` AS `agent_version`,
    `mp_clients`.`client_version` AS `client_version`,`mp_clients`.`agent_build` AS `agent_build`,
    `mp_clients`.`mdate` AS `mdate` ,
    `mp_clients_plist`.`EnableASUS` AS `EnableASUS`,
    `mp_clients_plist`.`MPDLTimeout` AS `MPDLTimeout`,`mp_clients_plist`.`AllowClient` AS `AllowClient`,
    `mp_clients_plist`.`MPServerSSL` AS `MPServerSSL`,`mp_clients_plist`.`Domain` AS `Domain`,
    `mp_clients_plist`.`Name` AS `Name`,`mp_clients_plist`.`MPInstallTimeout` AS `MPInstallTimeout`,
    `mp_clients_plist`.`MPServerDLLimit` AS `MPServerDLLimit`,`mp_clients_plist`.`PatchGroup` AS `PatchGroup`,
    `mp_clients_plist`.`MPProxyEnabled` AS `MPProxyEnabled`,`mp_clients_plist`.`Description` AS `Description`,
    `mp_clients_plist`.`MPDLConTimeout` AS `MPDLConTimeout`,`mp_clients_plist`.`MPProxyServerPort` AS `MPProxyServerPort`,
    `mp_clients_plist`.`MPProxyServerAddress` AS `MPProxyServerAddress`,`mp_clients_plist`.`AllowServer` AS `AllowServer`,
    `mp_clients_plist`.`MPServerAddress` AS `MPServerAddress`,`mp_clients_plist`.`MPServerPort` AS `MPServerPort`,
    `mp_clients_plist`.`MPServerTimeout` AS `MPServerTimeout`,`mp_clients_plist`.`Reboot` AS `Reboot`,
    `mp_clients_plist`.`DialogText` AS `DialogText`,`mp_clients_plist`.`PatchState` AS `PatchState`,
    `mpi_DirectoryServices`.`mpa_distinguishedName` AS `DistinguishedName`,
    substring_index(substring_index(`mpi_DirectoryServices`.`mpa_distinguishedName`,'OU=',-(1)),',',1) AS `AD-OU`
    from ((`mp_clients` left join `mp_clients_plist` on((`mp_clients`.`cuuid` = `mp_clients_plist`.`cuuid`)))
        left join `mpi_DirectoryServices` on((convert(`mp_clients`.`cuuid` using utf8) = `mpi_DirectoryServices`.`cuuid`)));
    '''
    op.execute(qstr)

    qstr1='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `mp_client_patches_apple_view` AS
    select `mpca`.`rid` AS `rid`,`mpca`.`cuuid` AS `cuuid`,`mpca`.`mdate` AS `date`,`mpca`.`patch` AS `patch`,
    `mpca`.`type` AS `type`,`mpca`.`description` AS `description`,`mpca`.`size` AS `size`,
    `mpca`.`recommended` AS `recommended`,`mpca`.`restart` AS `restart`,`ap`.`akey` AS `patch_id`
    from (`mp_client_patches_apple` `mpca` left join `apple_patches` `ap` on((`ap`.`supatchname` = `mpca`.`patch`)));
    '''
    op.execute(qstr1)

    qstr2='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `mp_client_patches_third_view` AS
    select `mpca`.`rid` AS `rid`,`mpca`.`cuuid` AS `cuuid`,`mpca`.`mdate` AS `date`,
    concat(`mpp`.`patch_name`,'-',`mpp`.`patch_ver`) AS `patch`,`mpca`.`type` AS `type`,
    `mpca`.`description` AS `description`,`mpca`.`size` AS `size`,`mpca`.`recommended` AS `recommended`,
    `mpca`.`restart` AS `restart`,`mpca`.`patch_id` AS `patch_id`
    from (`mp_client_patches_third` `mpca` join `mp_patches` `mpp` on((`mpp`.`puuid` = `mpca`.`patch_id`)));
    '''
    op.execute(qstr2)

    qstr3='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `mp_client_patches_full_view` AS
    select `mp_client_patches_apple_view`.`cuuid` AS `cuuid`,`mp_client_patches_apple_view`.`date` AS `date`,
    `mp_client_patches_apple_view`.`patch` AS `patch`,`mp_client_patches_apple_view`.`type` AS `type`,
    `mp_client_patches_apple_view`.`description` AS `description`,`mp_client_patches_apple_view`.`size` AS `size`,
    `mp_client_patches_apple_view`.`recommended` AS `recommended`,`mp_client_patches_apple_view`.`restart` AS `restart`,
    `mp_client_patches_apple_view`.`patch_id` AS `patch_id`
    from `mp_client_patches_apple_view` union select `mp_client_patches_third_view`.`cuuid` AS `cuuid`,
    `mp_client_patches_third_view`.`date` AS `date`,`mp_client_patches_third_view`.`patch` AS `patch`,
    `mp_client_patches_third_view`.`type` AS `type`,`mp_client_patches_third_view`.`description` AS `description`,
    `mp_client_patches_third_view`.`size` AS `size`,`mp_client_patches_third_view`.`recommended` AS `recommended`,
    `mp_client_patches_third_view`.`restart` AS `restart`,`mp_client_patches_third_view`.`patch_id` AS `patch_id`
    from `mp_client_patches_third_view`;
    '''
    op.execute(qstr3)

    qstr4='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `combined_patches_view` AS
    select distinct `ap`.`akey` AS `id`,`ap`.`patchname` AS `name`,`ap`.`version` AS `version`,
    `ap`.`postdate` AS `postdate`,`ap`.`title` AS `title`,
    (case when (`ap`.`restartaction` = 'NoRestart') then  'No' when (`ap`.`restartaction` = 'RequireRestart') then  'Yes' end) AS `reboot`,
     'Apple' AS `type`,`ap`.`supatchname` AS `suname`,1 AS `active`,`apa`.`severity` AS `severity`,
     `apa`.`patch_state` AS `patch_state`,`apa`.`patch_install_weight` AS `patch_install_weight`,
     `apa`.`patch_reboot` AS `patch_reboot_override`,0 AS `size`
     from (`apple_patches_mp_additions` `apa` left join `apple_patches` `ap`
        on((`ap`.`supatchname` = `apa`.`supatchname`)))
    union all select `mp_patches`.`puuid` AS `id`,`mp_patches`.`patch_name` AS `name`,`mp_patches`.`patch_ver` AS `version`,
    `mp_patches`.`cdate` AS `postdate`,`mp_patches`.`description` AS `title`,`mp_patches`.`patch_reboot` AS `reboot`,
    'Third' AS `type`,concat(`mp_patches`.`patch_name`,'-',`mp_patches`.`patch_ver`) AS `suname`,
    `mp_patches`.`active` AS `active`,`mp_patches`.`patch_severity` AS `severity`,`mp_patches`.`patch_state` AS `patch_state`,
    `mp_patches`.`patch_install_weight` AS `patch_install_weight`,
    (case when (`mp_patches`.`patch_reboot` = 'Yes') then  '1' when (`mp_patches`.`patch_reboot` = 'No') then  '0' end) AS `patch_reboot_override`,
    `mp_patches`.`pkg_size` AS `size` from `mp_patches`;
    '''
    op.execute(qstr4)

    qstr5='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `mp_client_patch_status_view` AS
    select `a`.`cuuid` AS `cuuid`,`a`.`date` AS `date`,`a`.`patch` AS `patch`,`a`.`type` AS `type`,
    `a`.`description` AS `description`,`a`.`size` AS `size`,`a`.`recommended` AS `recommended`,
    `a`.`restart` AS `restart`,`a`.`patch_id` AS `patch_id`,`cci`.`hostname` AS `hostname`,
    `cci`.`Domain` AS `ClientGroup`,`cci`.`ipaddr` AS `ipaddr`,`cci`.`PatchGroup` AS `PatchGroup`,
    (to_days(`a`.`date`) - to_days(`cpv`.`postdate`)) AS `DaysNeeded`
    from ((`mp_client_patches_full_view` `a` left join `combined_patches_view` `cpv`
     on((`cpv`.`id` = `a`.`patch_id`))) left join `mp_clients_view` `cci`
    on((`a`.`cuuid` = `cci`.`cuuid`))) where (`a`.`date` <>  '0000-00-00 00:00:00');
    '''
    op.execute(qstr5)

    qstr6='''CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `client_patch_status_view` AS select
    `a`.`cuuid` AS `cuuid`,`a`.`date` AS `date`,`a`.`patch` AS `patch`,`a`.`type` AS `type`,`a`.`description` AS `description`,
    `a`.`size` AS `size`,`a`.`recommended` AS `recommended`,`a`.`restart` AS `restart`,`a`.`patch_id` AS `patch_id`,
    `cci`.`hostname` AS `hostname`,`cci`.`Domain` AS `ClientGroup`,`cci`.`ipaddr` AS `ipaddr`,
    (to_days(`a`.`date`) - to_days(`cpv`.`postdate`)) AS `DaysNeeded`
    from ((`mp_client_patches_full_view` `a` left join `combined_patches_view` `cpv`
        on((`cpv`.`id` = `a`.`patch_id`))) left join `mp_clients_view` `cci` on((`a`.`cuuid` = `cci`.`cuuid`)))
    where (`a`.`date` <>  '0000-00-00 00:00:00');
    '''
    op.execute(qstr6)

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
	# Nothing
    ### end Alembic commands ###

    ### Drop MacPatch VIEWS ###
    op.execute("DROP VIEW IF EXISTS `mp_clients_view`;")
    op.execute("DROP VIEW IF EXISTS `mp_client_patches_apple_view`;")
    op.execute("DROP VIEW IF EXISTS `mp_client_patches_third_view`;")
    op.execute("DROP VIEW IF EXISTS `mp_client_patches_full_view`;")
    op.execute("DROP VIEW IF EXISTS `mp_client_patch_status_view`;")
    op.execute("DROP VIEW IF EXISTS `combined_patches_view`;")
    op.execute("DROP VIEW IF EXISTS `client_patch_status_view`;")