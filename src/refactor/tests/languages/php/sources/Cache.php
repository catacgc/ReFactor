<?php

namespace Mach;

use Mach\Config, Zend_Cache_Core;
use \Mach\Test;

/**
 * Zend Cache Core-Memcached proxy
 *
 * @author catacgc
 */
class Cache extends \Zend_Cache_Core implements Someinterface
{

    private static $_instance = null;
    private $_servers = array();

    public function __construct()
    {
        $cfg = Config::init();
        $cacheServers = $cfg->memcache->servers;

        foreach ($cacheServers as $server) {
            $port = 11211;
            if (strpos($server, ':') !== false) {
                list($server, $port) = explode(':', $server);
            }
            $this->_servers[] = array('host' => $server, 'port' => $port);
        }
		
		$cfg->loadConfig('test.ini', 'test');

        parent::__construct();
        $this->setBackend(new \Zend_Cache_Backend_Memcached(array('servers' => $this->_servers)));
        if(isset($cfg->site->name)) {
            $this->setNamespace($cfg->site->name);
        }
        if ($cfg->memcache->disabled) {
            $this->setOption('caching', false);
        }
    }

    /**
     * Get cache proxy
     *
     * @return \Mach\Cache
     */
    public static function getInstance()
    {
        if (!self::$_instance instanceof self) {
            self::$_instance = new self();
        }

        return self::$_instance;
    }

    /**
     * Sets a namespace for all cache entries
     * Usefull for avoid cache conflicts
     * @param string $string
     */
    public function setNamespace($string)
    {
        parent::setOption('cache_id_prefix', $string);
    }

    /**
     * Get the list of servers
     *
     * @return array - server list
     */
    public function getServers()
    {
        return $this->_servers;
    }

    /**
     * Save some data in a cache
     *
     * @param  mixed $data           Data to put in cache (can be another type than string if automatic_serialization is on)
     * @param  string $id             Cache id (if not set, the last cache id will be used)
     * @param  array $tags           Cache tags
     * @param  int $specificLifetime If != false, set a specific lifetime for this cache record (null => infinite lifetime)
     * @param  int   $priority         integer between 0 (very low priority) and 10 (maximum priority) used by some particular backends
     * @throws \Zend_Cache_Exception
     * @return boolean True if no problem
     */
    public function save($data, $id = null, $tags = array(), $specificLifetime = false, $priority = 8)
    {
        if (!is_string($data)) {
            $data = json_encode($data);
        }
        return parent::save($data, $id, $tags, $specificLifetime, $priority);
    }
    
    /**
     * Test if a cache is available for the given id and (if yes) return it (false else)
     *
     * @param  string  $id
     * @param  boolean $isJsonEncoded
     * @param  boolean $assoc
     * @return mixed
     */
    public function load($id, $isJsonEncoded = false, $assoc = true)
    {
        $data = parent::load($id);
        if ($data && $isJsonEncoded) {
            $data = json_decode($data, $assoc);
        }

        return $data;
    }

}
