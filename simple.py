import pyyatv

if __name__ == '__main__':
    regionId = '11212'
    tv = pyyatv.ChannelsParser(regionId, verbose=True)
    print(tv.url_channels)
    print(tv.getCurrentCity())
    channels = tv.getAllChannelsList()
    print('Channels', len(channels))
    for channel in channels:
        print(channel)
        progs = channel.getProgram()
        for prog in progs:
            print(prog)
